package main

import (
	"bufio"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"regexp"

	//"runtime/pprof"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

var (
	re  = regexp.MustCompile(`\D`)
	re1 = regexp.MustCompile(`^\D`)

	emuseatmap = map[string]string{}

	seatmap = map[string]string{
		"餐车":     "CA",
		"行李车":    "XL",
		"行邮车":    "XU",
		"邮政车":    "UZ",
		"空调发电车":  "KD",
		"发电车":    "KD", //# FD
		"硬座":     "YZ",
		"软座":     "RZ",
		"硬卧":     "YW",
		"软卧":     "RW",
		"双层硬座":   "SYZ",
		"双层软座":   "SRZ",
		"双层硬卧":   "SYW",
		"双层软卧":   "SRW",
		"包厢式硬卧":  "YW18", //# BY
		"高级软卧":   "RW19", //# GR
		"高级卧":    "WG",
		"一等半包":   "ZS", // RZBB
		"一等软座":   "RZ1",
		"二等软座":   "RZ2",
		"一等座":    "ZY",
		"二等座":    "ZE",
		"二等座一等座": "ZYE",
		"商务座":    "ZS",
		"特等座":    "ZT",
		"二等/餐车":  "ZEC",
		"二等座餐车":  "ZEC",
		"软卧餐车":   "WRC",
		"一等/商务座": "ZYS",
		"一等座商务座": "ZYS",
		"商务座一等座": "ZYS",
		"二等/商务座": "ZES",
		"商务座二等座": "ZES",
		"二等座商务座": "ZES",
		"一等/特等座": "ZYT",
		"一等座特等座": "ZYT",
		"二等/特等座": "ZET",
		"二等座特等座": "ZET",
	}

	d = map[byte]int{
		'Z': 10000, 'T': 20000, 'K': 30000,
		'Y': 00000,
		'G': 40000, 'D': 50000, 'C': 60000,
		'S': 70000,
		'L': 80000, 'A': 80000, 'N': 80000,
		'P': 10000, 'Q': 20000, 'W': 30000,
		'I': 50000,
		'V': 1000, 'B': 2000, 'U': 4000, 'X': 5000,
	}
)

func ReadCsv(fn string) [][]string {
	f, err := os.Open(fn)
	if err != nil {
		return [][]string{}
	}
	defer f.Close()

	bom := make([]byte, 3)
	f.Read(bom)
	if string(bom) != "\xEF\xBB\xBF" {
		f.Seek(0, 0)
	}

	r := csv.NewReader(f)
	ret, err := r.ReadAll()
	if err != nil {
		fmt.Fprintf(os.Stderr, "err=%+v\n", err)
	}
	return ret
}

func WriteCsv(fn string, data [][]string) error {
	f, err := os.OpenFile(fn, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666)
	if err != nil {
		return err
	}
	defer f.Close()
	f.WriteString("\xEF\xBB\xBF")

	w := csv.NewWriter(f)
	w.WriteAll(data)
	w.Flush()
	return nil
}

func WriteMinCsv(fn string, rows [][]string) error {
	f, err := os.OpenFile(fn, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666)
	if err != nil {
		return err
	}
	defer f.Close()

	f.WriteString("\xEF\xBB\xBF")

	w := bufio.NewWriter(f)
	for _, row := range rows {
		w.WriteString(strings.TrimRight(strings.Join(row, ","), ",") + "\n")
	}
	w.Flush()
	return nil
}

func ReadByte(fn string) []byte {
	bytes, err := ioutil.ReadFile(fn)
	if err != nil {
		return []byte{}
	}
	return bytes
}

func globdetail() []string {
	path := "detail/detail_*.json"
	matches, _ := filepath.Glob(path)
	fmt.Fprintf(os.Stderr, "find %d files for %s\n", len(matches), path)
	return matches
}

func getmin(s string) int {
	var h, m int
	resp, err := fmt.Sscanf(s, "%d:%d", &h, &m)
	fmt.Println(resp, err, h, m)
	if resp != 2 || err != nil {
		return -1
	}
	return h*60 + m
}

func getminhhmm(s string) int {
	if len(s) != 4 {
		return -1
	}
	h, _ := strconv.Atoi(s[0:2])
	m, _ := strconv.Atoi(s[2:4])
	return h*60 + m
}

func RetainNumber(s string) string {
	//re := regexp.MustCompile("\\D")
	return re.ReplaceAllString(s, "")
}

type SeatCap struct {
	CoachNo  string `json:"coachNo"`
	SeatType string `json:"seatType"`
	Capacity string `json:"capacity"`
	//CoachImageURL string `json:"coachImageUrl"` //
	//PowerType     string `json:"powerType"` //
}

type SeatCapSortCoachNo []SeatCap

func (s SeatCapSortCoachNo) Len() int {
	return len(s)
}
func (s SeatCapSortCoachNo) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}
func (s SeatCapSortCoachNo) Less(i, j int) bool {
	if s[i].CoachNo < s[j].CoachNo {
		return true
	}

	return false
}

func seats(List []SeatCap) string {
	ret := []string{}
	for _, x := range List {
		cur_seat := seatmap[x.SeatType]
		if len(cur_seat) == 0 {
			cur_seat = x.SeatType
		}
		cur_cap := RetainNumber(x.Capacity)
		ret = append(
			ret,
			fmt.Sprintf("%s(%s)",
				//x.CoachNo,
				cur_seat,
				cur_cap,
			),
		)
	}
	return strings.Join(ret, "_")
}

func seatcaps(List []SeatCap) string {
	ret := make([]string, 0, 32)
	num := 0
	last_seat := ""
	last_cap := ""
	for i, x := range List {
		cur_seat := seatmap[x.SeatType]
		if len(cur_seat) == 0 {
			cur_seat = x.SeatType
		}
		cur_cap := RetainNumber(x.Capacity)
		if ((cur_seat != last_seat) || (cur_cap != last_cap)) && i > 0 {
			numstr := ""
			if num > 1 {
				numstr = strconv.Itoa(num)
			}
			ret = append(ret,
				fmt.Sprintf("%s%s(%s)",
					numstr,
					last_seat,
					last_cap,
				),
			)
			num = 0
		}
		last_seat = cur_seat
		last_cap = cur_cap
		num += 1
	}
	numstr := ""
	if num > 1 {
		numstr = strconv.Itoa(num)
	}
	ret = append(ret,
		fmt.Sprintf("%s%s(%s)",
			numstr,
			last_seat,
			last_cap,
		),
	)
	return strings.Join(ret, "+")
}

type TrainDetail struct {
	//Timestamp string `json:"timestamp"`
	Status int `json:"status"`
	Data   struct {
		//OnTimePercent    string `json:"onTimePercent"`
		TrainsetTypeInfo struct {
			TrainsetTypeName string `json:"trainsetTypeName"` //
			TrainsetType     string `json:"trainsetType"`
			//TrainsetTypeImgURL string `json:"trainsetTypeImgUrl"`
			//TrainsetTypeAllImgURL string `json:"trainsetTypeAllImgUrl"` //
			//NetworkType        string `json:"networkType"`
			//MealCoach          string `json:"mealCoach"`
			//MaxSpeed string `json:"maxSpeed"` //
			//CurrentSpeed       string `json:"currentSpeed"`
			//CoachCount         string `json:"coachCount"`
			Capacity string `json:"capacity"`
			//FullLength string `json:"fullLength"` //
			//CoachOrganization  string `json:"coachOrganization"`
			First  []SeatCap `json:"first"`
			Second []SeatCap `json:"second"` //
		} `json:"trainsetTypeInfo"`
		StopTime []struct {
			TrainDate          string `json:"trainDate"`
			StartDate          string `json:"startDate"`
			StopDate           string `json:"stopDate"`
			TrainNo            string `json:"trainNo"`
			StationNo          string `json:"stationNo"`
			StationName        string `json:"stationName"`
			BureauCode         string `json:"bureauCode"`
			StationTelecode    string `json:"stationTelecode"`
			StationTrainCode   string `json:"stationTrainCode"`
			DayDifference      int    `json:"dayDifference"`
			ArriveTime         string `json:"arriveTime"`
			ArriveTimestamp    int64  `json:"arriveTimestamp"`
			StartTime          string `json:"startTime"`
			StartTimestamp     int64  `json:"startTimestamp"`
			TicketDelay        int    `json:"ticketDelay"`
			Lat                string `json:"lat"`
			Lon                string `json:"lon"`
			AreaCode           string `json:"areaCode"`
			Speed              string `json:"speed"`
			Distance           int    `json:"distance"`
			TimeSpan           string `json:"timeSpan"`
			OneStationCrossDay bool   `json:"oneStationCrossDay"`
		} `json:"stopTime"`
		RunStatus map[string][]int `json:"runStatus"`
	} `json:"data"`
}

func detaillocal(fn string) TrainDetail {
	var Detail TrainDetail
	json.Unmarshal(ReadByte(fn), &Detail)
	return Detail
}

func detailcsv(d TrainDetail) [][]string {
	ret := make([][]string, 0, 8)

	head := []string{
		d.Data.StopTime[0].TrainNo,
		//d.Data.StopTime[0].StationTelecode,
		//d.Data.StopTime[len(d.Data.StopTime)-1].StationTelecode,
		strings.TrimPrefix(d.Data.StopTime[0].StartDate, "20"),
		strings.TrimPrefix(d.Data.StopTime[0].StopDate, "20"),
		//d.Data.TrainsetTypeInfo.TrainsetType,
		RetainNumber(d.Data.TrainsetTypeInfo.Capacity),
	}

	if len(d.Data.TrainsetTypeInfo.First) > 0 {
		//if len(d.Data.TrainsetTypeInfo.TrainsetTypeName) > 0 {
		//	head = append(d.Data.TrainsetTypeInfo.TrainsetTypeName)
		//}

		isEmu := false
		if strings.ContainsAny(d.Data.StopTime[0].TrainNo[5:10], "GDCS") {
			isEmu = true
			key := hash_no(strings.TrimLeft(d.Data.StopTime[0].TrainNo[5:10], "0"))
			if key/100 == 702 ||
				key/100 == 706 ||
				key/100 == 709 {
				isEmu = false
			}
		}
		if isEmu {
			// head = append(head, seats(d.Data.TrainsetTypeInfo.First))
			sort.Stable(SeatCapSortCoachNo(d.Data.TrainsetTypeInfo.First))

			emuseat := seats(d.Data.TrainsetTypeInfo.First)
			emuseattype := emuseatmap[emuseat]
			if emuseattype == "" {
				emuseattype = emuseat
				//fmt.Printf("%s: %s not found emuseattype\n", d.Data.StopTime[0].TrainNo, emuseat)
				// panic("") // TODO
			}
			head = append(head, emuseattype)
		} else {
			head = append(head, seatcaps(d.Data.TrainsetTypeInfo.First))
		}
	}

	ret = append(ret, head)

	//lastArriveTime := ""
	lastStartTime := ""
	lastDistance := 0
	lastTrainCode := ""
	lastDayDiff := 0
	for i, st := range d.Data.StopTime {
		ChangeTrainCode := ""
		if st.StationTrainCode != lastTrainCode {
			ChangeTrainCode = st.StationTrainCode
		}

		ChangeDay := ""
		if st.DayDifference != lastDayDiff {
			ChangeDay = fmt.Sprintf("%+d", st.DayDifference)
		}

		StopTime := getminhhmm(st.StartTime) - getminhhmm(st.ArriveTime)
		if StopTime < 0 {
			StopTime += 1440
		}
		StopTimeStr := strconv.Itoa(StopTime)
		if i == 0 {
			StopTimeStr = st.StartTime
		}
		if i == len(d.Data.StopTime)-1 {
			StopTimeStr = ""
		}

		RunTimeStr := ""
		if i > 0 {
			RunTime := getminhhmm(st.ArriveTime) - getminhhmm(lastStartTime) + (st.DayDifference-lastDayDiff)*1440
			if st.OneStationCrossDay {
				RunTime -= 1440
			}
			RunTimeStr = strconv.Itoa(RunTime)
		}

		ret = append(
			ret,
			[]string{
				st.StationTelecode,
				//st.StationName,
				//st.StationNo,
				//st.DayDifference-st.OneStationCrossDay,
				RunTimeStr, // st.ArriveTime
				//st.DayDifference,
				StopTimeStr,                              // st.StartTime,
				strconv.Itoa(st.Distance - lastDistance), // strconv.Itoa(st.Distance),
				// RetainNumber(st.Speed), //
				//st.TrainNo,
				ChangeTrainCode,
				ChangeDay,
			},
		)

		//lastArriveTime = st.ArriveTime
		lastStartTime = st.StartTime
		lastDistance = st.Distance
		lastTrainCode = st.StationTrainCode
		lastDayDiff = st.DayDifference
	}

	return ret
}

type Seat struct {
	TrainNo      string `json:"trainNo"`
	TrainGroupNo int    `json:"trainGroupNo"`
	CoachNo      string `json:"coachNo"`
	CoachType    string `json:"coachType"`
	Limit1       int    `json:"limit1"`
	Limit2       int    `json:"limit2"`
	CommentCode  string `json:"commentCode"` //
	SeatFeature  string `json:"seatFeature"` // 0 非空调 1 自发电空调 3 新空调
	StartDate    string `json:"startDate"`
	StopDate     string `json:"stopDate"`
	Origin       string `json:"origin"`
	RunningStyle int    `json:"runningStyle"`
	RunningRule  int    `json:"runningRule"`
}
type CompileList struct {
	// Timestamp int64 `json:"timestamp"`
	Status int    `json:"status"`
	Data   []Seat `json:"data"`
}

type SeatSort []Seat

func (s SeatSort) Len() int {
	return len(s)
}
func (s SeatSort) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}
func (s SeatSort) Less(i, j int) bool {
	if s[i].StartDate != s[j].StartDate {
		return s[i].StartDate < s[j].StartDate
	}

	if s[i].CoachNo != s[j].CoachNo {
		return s[i].CoachNo < s[j].CoachNo
	}

	return false
}

func compilelistlocal(fn string) CompileList {
	var List CompileList
	json.Unmarshal(ReadByte(fn), &List)
	return List
}

func compilelistcsv(l CompileList) [][]string {
	ret := make([][]string, 0, 8)

	sort.Stable(SeatSort(l.Data))

	for i, car := range l.Data {
		limit := ""
		if car.Limit1 > 0 {
			limit = strconv.Itoa(car.Limit1)
		}
		if car.Limit2 > 0 {
			limit += "/" + strconv.Itoa(car.Limit2)
		}

		seatfeature := ""
		if car.SeatFeature != "3" {
			seatfeature = car.SeatFeature
		}

		row := []string{
			// car.TrainGroupNo,
			car.CoachNo,
			strings.TrimRight(car.CoachType, " "),
			limit,
			strings.TrimRight(car.CommentCode, " "),
			seatfeature,
		}

		if i == 0 {
			row = append(row,
				car.TrainNo,
				strings.TrimPrefix(car.StartDate, "20"),
				strings.TrimPrefix(car.StopDate, "20"),
			)
		}

		ret = append(
			ret,
			row,
		)
	}

	return ret
}

func hash_no(s string) int {
	train_class := d[s[0]]
	n, _ := strconv.Atoi(re1.ReplaceAllString(s, ""))
	return train_class + n
}

type Event struct {
	rw            [16]sync.Mutex
	wg            sync.WaitGroup
	fns           []string
	tables        [][][][]string
	tablesCompile [][][][]string
	ret           [][]string
	ret2          [][]string
	ret3          [][]string
	cur           int32
	limit         int32
}

func (e *Event) AddMapThread(id int) {
	var st, ed, part int32
	part = 1000
	for st < e.limit {
		ed = atomic.AddInt32(&e.cur, part)
		st = ed - part
		if st > e.limit {
			break
		}
		if ed > e.limit {
			ed = e.limit
		}
		// fmt.Fprintf(os.Stderr, "run   %2d %9d %9d %9d|%s\n", id, st, ed, ed-st, strings.Repeat(" ", id)+"+")
		// t0 := time.Now().UnixNano()
		for i := st; i < ed; i++ {
			fn := e.fns[i]
			c := detailcsv(detaillocal(fn))
			fncompile := strings.ReplaceAll(fn, "detail\\detail", "list/list") //  fmt.Sprintf("list/list_%s.json", c[0][0])
			compile := compilelistcsv(compilelistlocal(fncompile))
			key := hash_no(strings.TrimLeft(c[0][0][5:10], "0"))

			// if len(compile) > 0 && (c[0][2] != compile[0][7]) { // c[0][1] != compile[0][6] ||
			// 	if fmt.Sprintf("list/list_%s.json", c[0][0]) != fncompile {
			// 		fmt.Printf("# ")
			// 	}
			// 	if c[0][2] > "231231" && compile[0][7] < "231231" {
			// 		//fmt.Printf("getcompilelist('%s',cache=0)\n", c[0][0])
			// 		//} else {
			// 		fmt.Printf("getdetail('%s', '%s', '%s',cache=0)\n", c[1][0], c[0][0], "20"+compile[0][7])
			// 	}
			// } else if len(compile) > 1 && (c[0][1] != compile[0][6]) {
			// 	if fmt.Sprintf("list/list_%s.json", c[0][0]) != fncompile {
			// 		fmt.Printf("# ")
			// 	}
			// 	fmt.Printf("#### getcompilelist('%s',cache=0)\n", c[0][0])
			// }

			serviceTypeMap := make(map[string]int, 1)
			for _, row := range compile {
				serviceType := "3"
				if len(row) > 4 {
					serviceType = row[4]
				}
				serviceTypeMap[serviceType]++
			}
			serviceTypeArr := []string{}
			for serviceType := range serviceTypeMap {
				serviceTypeArr = append(serviceTypeArr, serviceType)
			}
			sort.Strings(serviceTypeArr)
			serviceTypes := strings.Join(serviceTypeArr, "|")

			if serviceTypes != "3" { // most serviceType
				c[0] = append(c[0], serviceTypes)
			}

			e.rw[key&0x0f].Lock()

			if e.tables[key] == nil {
				e.tables[key] = make([][][]string, 0, 8)
			}
			e.tables[key] = append(e.tables[key], c)

			if e.tablesCompile[key] == nil {
				e.tablesCompile[key] = make([][][]string, 0, 18)
			}
			e.tablesCompile[key] = append(e.tablesCompile[key], compile)

			e.rw[key&0x0f].Unlock()

			c = nil
		}
		// t1 := time.Now().UnixNano()
		// fmt.Fprintf(os.Stderr, "done  %2d %9d %9d %9d|%s %10d\n", id, st, ed, ed-st, strings.Repeat(" ", id)+"_"+strings.Repeat(" ", 24-id), (t1-t0)/1e+6)
	}

	e.wg.Done()
}

type Cmpby1_0 [][][]string

func (s Cmpby1_0) Len() int {
	return len(s)
}
func (s Cmpby1_0) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}
func (s Cmpby1_0) Less(i, j int) bool {
	if len(s[i]) < 1 {
		return false
	}
	if len(s[j]) < 1 {
		return false
	}
	if len(s[i][0]) < 3 {
		return false
	}
	if len(s[j][0]) < 3 {
		return false
	}

	date1 := s[i][0][1]
	date2 := s[j][0][1]
	if date1 > date2 {
		return false
	}
	if date1 < date2 {
		return true
	}

	if s[i][0][0] > s[j][0][0] {
		return false
	}
	if s[i][0][0] < s[j][0][0] {
		return true
	}

	return false
}

type Cmpby6_5 [][][]string

func (s Cmpby6_5) Len() int {
	return len(s)
}
func (s Cmpby6_5) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}
func (s Cmpby6_5) Less(i, j int) bool {
	if len(s[i]) < 1 {
		return false
	}
	if len(s[j]) < 1 {
		return false
	}
	if len(s[i][0]) < 8 {
		return false
	}
	if len(s[j][0]) < 8 {
		return false
	}

	date1 := s[i][0][6]
	date2 := s[j][0][6]
	if date1 > date2 {
		return false
	}
	if date1 < date2 {
		return true
	}

	if s[i][0][5] > s[j][0][5] {
		return false
	}
	if s[i][0][5] < s[j][0][5] {
		return true
	}

	return false
}

func (e *Event) SortThread(id int) {
	var st, ed, part int32
	part = 100
	for st < e.limit {
		ed = atomic.AddInt32(&e.cur, part)
		st = ed - part
		if st > e.limit {
			break
		}
		if ed > e.limit {
			ed = e.limit
		}
		//fmt.Fprintf(os.Stderr, "run   %2d %9d %9d %9d|%s\n", id, st, ed, ed-st, strings.Repeat(" ", id)+"+")
		//t0 := time.Now().UnixNano()
		for key := st; key < ed; key++ {
			if len(e.tables[key]) >= 2 {
				sort.Stable(Cmpby1_0(e.tables[key]))
			}
			//fmt.Fprintf(os.Stderr, "%d len:%d\n", key, len(e.tables[key]))

			if len(e.tablesCompile[key]) >= 2 {
				sort.Stable(Cmpby6_5(e.tablesCompile[key]))
			}
		}
		//t1 := time.Now().UnixNano()
		//fmt.Fprintf(os.Stderr, "done  %2d %9d %9d %9d|%s %10d\n", id, st, ed, ed-st, strings.Repeat(" ", id)+"_"+strings.Repeat(" ", 24-id), (t1-t0)/1E+6)
	}

	e.wg.Done()
}

func CompareTime(a1, a2 [][]string) bool {
	if len(a1) != len(a2) {
		return false
	}
	//for _, j := range []int{1, 2, 0, 3, 4, 5} {
	for _, j := range []int{1, 2, 0} {
		//if len(a1[i]) != len(a2[i]):
		//return 0
		for i := 1; i < len(a1); i++ {
			if a1[i][j] != a2[i][j] {
				return false
			}
		}
	}
	return true
}

func (e *Event) JoinThread(id int) {
	var st, ed, part int32
	part = 1000
	for st < e.limit {
		ed = atomic.AddInt32(&e.cur, part)
		st = ed - part
		if st > e.limit {
			break
		}
		if ed > e.limit {
			ed = e.limit
		}
		//fmt.Fprintf(os.Stderr, "run   %2d %9d %9d %9d|%s\n", id, st, ed, ed-st, strings.Repeat(" ", id)+"+")
		//t0 := time.Now().UnixNano()
		for key := st; key < ed; key++ {
			l := len(e.tables[key])
			if l == 0 {
				continue
			}
			//fmt.Fprintf(os.Stderr, "%d len:%d\n", key, len(e.tables[key]))
			e.rw[0].Lock()
			for i, table := range e.tables[key] {
				e.ret2 = append(e.ret2, append([]string{table[0][0], table[1][0], table[len(table)-1][0]}, table[0][1:]...))
				if i+1 < l && CompareTime(table, e.tables[key][i+1]) {
					e.ret = append(e.ret, table[0])
				} else {
					e.ret = append(e.ret, table...)
					e.ret = append(e.ret, []string{})
				}
			}

			for _, tableCompile := range e.tablesCompile[key] {
				e.ret3 = append(e.ret3, tableCompile...)
			}

			e.rw[0].Unlock()
		}
		//t1 := time.Now().UnixNano()
		//fmt.Fprintf(os.Stderr, "done  %2d %9d %9d %9d|%s %10d\n", id, st, ed, ed-st, strings.Repeat(" ", id)+"_"+strings.Repeat(" ", 24-id), (t1-t0)/1E+6)
	}

	e.wg.Done()
}

func init() {
	//
}

func main() {
	/*
			cpuProfile := "cpu.pprof"
		    memProfile := "mem.pprof"
		    //采样cpu运行状态
		    if cpuProfile != "" {
		        f, err := os.Create(cpuProfile)
		        if err != nil {
		            //log.Fatal(err)
		        }
		        pprof.StartCPUProfile(f)
		        defer pprof.StopCPUProfile()
			}
	*/

	rows := ReadCsv("车型1.csv")
	// fmt.Println(rows)
	rows = append(rows,
		strings.Split(",RZ1(64)_RZ2(91)_RZ2(91)_CA(58)_RZ2(91)_RZ2(85)_RZ2(91)_RZ1(64),1A-250 1121-1166,1A-250 1121-1166", ","),
		strings.Split(",RZ1(72)_RZ2(101)_RZ2(101)_RZ2(101)_CA(19)_RZ2(101)_RZ2(101)_RZ1(72),1A-250 1167-1168,1A-250 1167-1168", ","),
		strings.Split(",RZ2(55)_RZ2(100)_RZ2(85)_RZ2(100)_CA(55)_RZ2(100)_RZ1(51)_RZ2(64),2,2A非统 2C-1", ","),
		strings.Split(",RZ2(55)_RZ2(100)_RZ2(85)_RZ2(100)_CA(54)_RZ2(100)_RZ1(51)_RZ2(65),2C-2", ","),
		strings.Split(",RW(40)_RW(60)_RW(60)_RW(60)_RW(60)_RW(60)_RW(60)_RW(60)_CA(0)_RW(60)_RW(60)_RW(60)_RW(60)_RW(60)_RW(60)_RW(40),2E 2463-2465,新2E 纵向 2463-2465", ","),
		strings.Split(",RZ2(74)_RZ2(93)_RZ2(93)_RZ2(93)_RZ2(93)_RZ2(42)_RZ2(74)_RZ1(60),5A#1,5001-5013 5044-5045", ","),
		strings.Split(",RZ2(44)_RZ2(64)_RZ2(64)_RZ2(64)_CA(64)_RZ2(64)_RZ2(64)_RZ2(44),6A", ","),
		strings.Split(",RZ1(48)_RZ2(87)_RZ2(87)_RZ2(87)_CA(54)_RZ2(87)_RZ2(87)_RZ2(76),6A广深", ","),

		strings.Split(",RZ2(46)_RZ2(85)_RZ1(44)_RZ1(51)_RZ2(38)_RZ2(85)_RZ2(85)_RZ2(46),A?,A非统 ZET?", ","),
		strings.Split(",RZ2(46)_RZ2(85)_RZ1(44)_RZ1(51)_RZ2(52)_RZ2(85)_RZ2(85)_RZ2(46),A,A非统 ZET?", ","),
		strings.Split(",RZ1(27)_RZ1(56)_RZ1(24)_RZ1(56)_RZ2(73)_RZ2(85)_RZ2(85)_RZ2(85)_CA(38)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ1(27),AL", ","),
		strings.Split(",RZ1(27)_RZ1(56)_RZ1(24)_RZ1(56)_RZ2(73)_RZ2(85)_RZ2(85)_RZ2(85)_CA(0)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ1(27),AL", ","),
		strings.Split(",RZ1(13)_RZ1(56)_RZ1(56)_RZ2(85)_RZ2(73)_RZ2(85)_RZ2(85)_RZ2(85)_CA(0)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ2(85)_RZ1(13),AL统,AL-2 3 统", ","),
		strings.Split(",RZ1(39)_RZ1(56)_ZS(24)_RZ1(56)_RZ2(71)_RZ2(80)_RZ2(80)_RZ2(80)_CA(38)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ1(39),BL", ","),
		strings.Split(",RZ1(39)_RZ1(56)_ZS(24)_RZ1(56)_RZ2(71)_RZ2(80)_RZ2(80)_RZ2(80)_CA(0)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ1(39),BL", ","),
		strings.Split(",RZ1(16)_RZ1(56)_RZ1(56)_RZ2(80)_RZ2(71)_RZ2(80)_RZ2(80)_RZ2(80)_CA(38)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ1(16),BL统,BL-2 3 CL 统", ","),
		strings.Split(",RZ1(16)_RZ1(56)_RZ1(56)_RZ2(80)_RZ2(71)_RZ2(80)_RZ2(80)_RZ2(80)_CA(0)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ2(80)_RZ1(16),BL统,BL-2 3 CL 统", ","),
		strings.Split(",RZ1(38)_RZ2(84)_RZ2(84)_CA(59)_RZ2(84)_RZ2(81)_RZ2(84)_RZ2(54),380D", ","),
		strings.Split(",RZ1(38)_RZ2(84)_RZ2(84)_CA(45)_RZ2(84)_RZ2(81)_RZ2(84)_RZ2(54),380D?", ","),
	)
	for _, row := range rows {
		if len(row) <= 2 {
			continue
		}
		if len(row[1]) == 0 {
			continue
		}

		emuseatmap[row[1]] = row[2]
		key := row[1]
		key = strings.ReplaceAll(key, "+", "_")

		car_num := len(strings.Split(key, "_"))

		key = strings.ReplaceAll(key, "ZYS", "RZ1")
		key = strings.ReplaceAll(key, "ZYT", "RZ1")
		key = strings.ReplaceAll(key, "ZES", "RZ2")
		key = strings.ReplaceAll(key, "ZET", "RZ2")
		key = strings.ReplaceAll(key, "ZEC", "CA")
		key = strings.ReplaceAll(key, "ZY", "RZ1")
		key = strings.ReplaceAll(key, "ZE", "RZ2")

		for i := 0; i < (1 << 2); i++ {
			key1 := key
			if i&(1<<0) > 0 {
				key1 = strings.ReplaceAll(key1, "CA", "RZ2")
			}

			if i&(1<<1) > 0 {
				key1 = strings.ReplaceAll(key1, "ZS", "RZ1")
			}

			emuseatmap[key1] = row[2]
			if car_num == 8 {
				emuseatmap[key1+"_"+key1] = row[2] + "_" + row[2]
			}
			// fmt.Println(key1, row[2])
		}

	}

	maxlen := 90000
	var e Event
	e.fns = globdetail()
	e.tables = make([][][][]string, maxlen)
	e.tablesCompile = make([][][][]string, maxlen)
	//e.rw = make([]sync.Mutex, 16)

	var t0, t1 int64
	t0 = time.Now().UnixNano()
	e.limit = int32(len(e.fns))
	threadnum := 12
	e.wg.Add(threadnum)
	for id := 0; id < threadnum; id++ {
		go e.AddMapThread(id)
	}
	e.wg.Wait()
	t1 = time.Now().UnixNano()
	fmt.Fprintf(os.Stderr, "%6d.%06d ms read + process\n", (t1-t0)/1e6, (t1-t0)%1e6)
	fmt.Fprintf(os.Stderr, "len %10d train\n", len(e.fns))

	e.fns = nil

	t0 = time.Now().UnixNano()
	e.cur = 0
	e.limit = int32(maxlen)
	threadnum = 6
	e.wg.Add(threadnum)
	for id := 0; id < threadnum; id++ {
		go e.SortThread(id)
	}
	e.wg.Wait()
	t1 = time.Now().UnixNano()
	fmt.Fprintf(os.Stderr, "%6d.%06d ms sort\n", (t1-t0)/1e6, (t1-t0)%1e6)

	t0 = time.Now().UnixNano()
	e.cur = 0
	e.limit = int32(maxlen)
	e.ret = make([][]string, 0, 2525684)
	e.ret2 = make([][]string, 0, 307200)
	threadnum = 1
	e.wg.Add(threadnum)
	for id := 0; id < threadnum; id++ {
		go e.JoinThread(id)
	}
	e.wg.Wait()
	t1 = time.Now().UnixNano()
	fmt.Fprintf(os.Stderr, "%6d.%06d ms join\n", (t1-t0)/1e6, (t1-t0)%1e6)

	/*
		if memProfile != "" {
			f, err := os.Create(memProfile)
			if err != nil {
				//log.Fatal(err)
			}
			pprof.WriteHeapProfile(f)
			f.Close()
		}
	*/

	// e.tables = nil
	// time.Sleep(20 * time.Second)

	t0 = time.Now().UnixNano()
	WriteMinCsv("js/time_detail.csv", e.ret)
	t1 = time.Now().UnixNano()
	fmt.Fprintf(os.Stderr, "%6d.%06d ms write\n", (t1-t0)/1e6, (t1-t0)%1e6)
	t0 = time.Now().UnixNano()
	WriteMinCsv("js/train_detail.csv", e.ret2)
	t1 = time.Now().UnixNano()
	fmt.Fprintf(os.Stderr, "%6d.%06d ms write\n", (t1-t0)/1e6, (t1-t0)%1e6)
	t0 = time.Now().UnixNano()
	WriteMinCsv("js/compilelist.csv", e.ret3)
	t1 = time.Now().UnixNano()
	fmt.Fprintf(os.Stderr, "%6d.%06d ms write\n", (t1-t0)/1e6, (t1-t0)%1e6)

	fmt.Fprintf(os.Stderr, "len %10d line\n", len(e.ret))
	//fmt.Fprintf(os.Stderr, "%v\n", e.tables[10001])

}
