package main

var VALS = map[byte]int{
	'I': 1,
	'V': 5,
	'X': 10,
	'L': 50,
	'C': 100,
	'D': 500,
	'M': 1000,
}

func romanToInt(s string) int {
	return romanToInt_forward(s)
}

func romanToInt_forward(s string) (res int) {
	for i := range len(s) {
		curr := VALS[s[i]]
		res += curr
		if i > 0 {
			prev := VALS[s[i-1]]
			if prev < curr {
				// prev was added when it was curr and then curr was added
				// we need (curr-prev), have (curr+prev)
				// so subtract prev twice
				res -= prev + prev
			}
		}
	}
	return res
}

func romanToInt_backward(s string) (res int) {
	for i := len(s) - 1; i >= 0; i-- {
		curr := VALS[s[i]]
		res += curr
		if i > 0 {
			prev := VALS[s[i-1]]
			if prev < curr {
				res -= prev
				i--
			}
		}
	}
	return res
}

func main() {

}
