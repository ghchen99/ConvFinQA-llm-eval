## Example

```json
{
    "pre_text": [
        "( 1 ) includes shares repurchased through our publicly announced share repurchase program and shares tendered to pay the exercise price and tax withholding on employee stock options .",
        "shareowner return performance graph the following performance graph and related information shall not be deemed 201csoliciting material 201d or to be 201cfiled 201d with the securities and exchange commission , nor shall such information be incorporated by reference into any future filing under the securities act of 1933 or securities exchange act of 1934 , each as amended , except to the extent that the company specifically incorporates such information by reference into such filing .",
        "the following graph shows a five-year comparison of cumulative total shareowners 2019 returns for our class b common stock , the s&p 500 index , and the dow jones transportation average .",
        "the comparison of the total cumulative return on investment , which is the change in the quarterly stock price plus reinvested dividends for each of the quarterly periods , assumes that $ 100 was invested on december 31 , 2004 in the s&p 500 index , the dow jones transportation average , and our class b common stock .",
        "comparison of five year cumulative total return $ 40.00 $ 60.00 $ 80.00 $ 100.00 $ 120.00 $ 140.00 $ 160.00 2004 20092008200720062005 s&p 500 ups dj transport ."
    ],
    "post_text": [
        "."
    ],
    "filename": "UPS/2009/page_33.pdf",
    "table_ori": [
        [
            "",
            "12/31/04",
            "12/31/05",
            "12/31/06",
            "12/31/07",
            "12/31/08",
            "12/31/09"
        ],
        [
            "United Parcel Service, Inc.",
            "$100.00",
            "$89.49",
            "$91.06",
            "$87.88",
            "$70.48",
            "$75.95"
        ],
        [
            "S&P 500 Index",
            "$100.00",
            "$104.91",
            "$121.48",
            "$128.15",
            "$80.74",
            "$102.11"
        ],
        [
            "Dow Jones Transportation Average",
            "$100.00",
            "$111.65",
            "$122.61",
            "$124.35",
            "$97.72",
            "$115.88"
        ]
    ],
    "table": [
        [
            "",
            "12/31/04",
            "12/31/05",
            "12/31/06",
            "12/31/07",
            "12/31/08",
            "12/31/09"
        ],
        [
            "united parcel service inc .",
            "$ 100.00",
            "$ 89.49",
            "$ 91.06",
            "$ 87.88",
            "$ 70.48",
            "$ 75.95"
        ],
        [
            "s&p 500 index",
            "$ 100.00",
            "$ 104.91",
            "$ 121.48",
            "$ 128.15",
            "$ 80.74",
            "$ 102.11"
        ],
        [
            "dow jones transportation average",
            "$ 100.00",
            "$ 111.65",
            "$ 122.61",
            "$ 124.35",
            "$ 97.72",
            "$ 115.88"
        ]
    ],
    "id": "Double_UPS/2009/page_33.pdf",
    "annotation": {
        "amt_table": "<table class='wikitable'><tr><td>1</td><td></td><td>12/31/04</td><td>12/31/05</td><td>12/31/06</td><td>12/31/07</td><td>12/31/08</td><td>12/31/09</td></tr><tr><td>2</td><td>united parcel service inc .</td><td>$ 100.00</td><td>$ 89.49</td><td>$ 91.06</td><td>$ 87.88</td><td>$ 70.48</td><td>$ 75.95</td></tr><tr><td>3</td><td>s&p 500 index</td><td>$ 100.00</td><td>$ 104.91</td><td>$ 121.48</td><td>$ 128.15</td><td>$ 80.74</td><td>$ 102.11</td></tr><tr><td>4</td><td>dow jones transportation average</td><td>$ 100.00</td><td>$ 111.65</td><td>$ 122.61</td><td>$ 124.35</td><td>$ 97.72</td><td>$ 115.88</td></tr></table>",
        "amt_pre_text": "( 1 ) includes shares repurchased through our publicly announced share repurchase program and shares tendered to pay the exercise price and tax withholding on employee stock options . shareowner return performance graph the following performance graph and related information shall not be deemed 201csoliciting material 201d or to be 201cfiled 201d with the securities and exchange commission , nor shall such information be incorporated by reference into any future filing under the securities act of 1933 or securities exchange act of 1934 , each as amended , except to the extent that the company specifically incorporates such information by reference into such filing . the following graph shows a five-year comparison of cumulative total shareowners 2019 returns for our class b common stock , the s&p 500 index , and the dow jones transportation average . the comparison of the total cumulative return on investment , which is the change in the quarterly stock price plus reinvested dividends for each of the quarterly periods , assumes that $ 100 was invested on december 31 , 2004 in the s&p 500 index , the dow jones transportation average , and our class b common stock . comparison of five year cumulative total return $ 40.00 $ 60.00 $ 80.00 $ 100.00 $ 120.00 $ 140.00 $ 160.00 2004 20092008200720062005 s&p 500 ups dj transport .",
        "amt_post_text": ".",
        "original_program_0": "subtract(91.06, const_100), divide(#0, const_100)",
        "step_list_0": [
            "subtract(91.06, const_100)",
            "divide(#0, const_100)"
        ],
        "answer_list_0": [
            "#0",
            "#1"
        ],
        "original_program_1": "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100), divide(#2, const_100), subtract(#1, #3)",
        "step_list_1": [
            "subtract(75.95, const_100)",
            "divide(#0, const_100)",
            "subtract(102.11, const_100)",
            "divide(#2, const_100)",
            "subtract(#1, #3)"
        ],
        "answer_list_1": [
            "#0",
            "#1",
            "#2",
            "#3",
            "#4"
        ],
        "offset": 2,
        "step_list": [
            "subtract(91.06, const_100)",
            "divide(#0, const_100)",
            "subtract(75.95, const_100)",
            "divide(#2, const_100)",
            "subtract(102.11, const_100)",
            "divide(#4, const_100)",
            "subtract(#5, #5)"
        ],
        "answer_list": [
            "#0",
            "#1",
            "#2",
            "#3",
            "#4",
            "#5",
            "#6"
        ],
        "dialogue_break": [
            "what was the fluctuation of the performance price of the ups from 2004 to 2006?",
            "and how much does this fluctuation represent in relation to that price in 2004?",
            "and from this year to 2009, what was the fluctuation for that stock?",
            "what is this fluctuation as a percentage of the 2004 price?",
            "and for the s&p 500 index price, what was the fluctuation in those five years?",
            "and what percentage does this fluctuation represent in relation to the 2004 price of this stock?",
            "what is, then, the difference between the ups percentage and this s&p 500 index one, for this five year period?"
        ],
        "turn_program_ori": [
            "subtract(91.06, const_100)",
            "subtract(91.06, const_100), divide(#0, const_100)",
            "subtract(75.95, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100), divide(#2, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100), divide(#2, const_100), subtract(#1, #3)"
        ],
        "dialogue_break_ori": [
            "what was the fluctuation of the performance price of the ups from 2004 to 2006?",
            "and how much does this fluctuation represent in relation to that price in 2004?",
            "and from this year to 2009, what was the fluctuation for that stock?",
            "what is this fluctuation as a percentage of the 2004 price?",
            "and for the s&p 500 index price, what was the fluctuation in those five years?",
            "and what percentage does this fluctuation represent in relation to the 2004 price of this stock?",
            "what is, then, the difference between the ups percentage and this s&p 500 index one, for this five year period?"
        ],
        "turn_program": [
            "subtract(91.06, const_100)",
            "subtract(91.06, const_100), divide(#0, const_100)",
            "subtract(75.95, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100), divide(#2, const_100)",
            "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100), divide(#2, const_100), subtract(#1, #3)"
        ],
        "qa_split": [
            0,
            0,
            1,
            1,
            1,
            1,
            1
        ],
        "exe_ans_list": [
            -8.94,
            -0.0894,
            -24.05,
            -0.2405,
            2.11,
            0.0211,
            -0.2616
        ]
    },
    "qa_0": {
        "question": "what is the roi of an investment in ups in 2004 and sold in 2006?",
        "answer": "-8.9%",
        "explanation": "",
        "ann_table_rows": [
            1
        ],
        "ann_text_rows": [],
        "steps": [
            {
                "op": "minus1-1",
                "arg1": "91.06",
                "arg2": "const_100",
                "res": "-8.94"
            },
            {
                "op": "divide1-2",
                "arg1": "#0",
                "arg2": "const_100",
                "res": "-8.9%"
            }
        ],
        "program": "subtract(91.06, const_100), divide(#0, const_100)",
        "gold_inds": {
            "table_1": "the united parcel service inc . of 12/31/04 is $ 100.00 ; the united parcel service inc . of 12/31/05 is $ 89.49 ; the united parcel service inc . of 12/31/06 is $ 91.06 ; the united parcel service inc . of 12/31/07 is $ 87.88 ; the united parcel service inc . of 12/31/08 is $ 70.48 ; the united parcel service inc . of 12/31/09 is $ 75.95 ;"
        },
        "exe_ans": -0.0894,
        "program_re": "divide(subtract(91.06, const_100), const_100)"
    },
    "qa_1": {
        "question": "what was the difference in percentage cumulative return on investment for united parcel service inc . compared to the s&p 500 index for the five year period ended 12/31/09?",
        "answer": "-26.16%",
        "explanation": "",
        "ann_table_rows": [
            1,
            2
        ],
        "ann_text_rows": [],
        "steps": [
            {
                "op": "minus2-1",
                "arg1": "75.95",
                "arg2": "const_100",
                "res": "-24.05"
            },
            {
                "op": "divide2-2",
                "arg1": "#0",
                "arg2": "const_100",
                "res": "-24.05%"
            },
            {
                "op": "minus2-3",
                "arg1": "102.11",
                "arg2": "const_100",
                "res": "2.11"
            },
            {
                "op": "divide2-4",
                "arg1": "#2",
                "arg2": "const_100",
                "res": "2.11%"
            },
            {
                "op": "minus2-5",
                "arg1": "#1",
                "arg2": "#3",
                "res": "-26.16%"
            }
        ],
        "program": "subtract(75.95, const_100), divide(#0, const_100), subtract(102.11, const_100), divide(#2, const_100), subtract(#1, #3)",
        "gold_inds": {
            "table_1": "the united parcel service inc . of 12/31/04 is $ 100.00 ; the united parcel service inc . of 12/31/05 is $ 89.49 ; the united parcel service inc . of 12/31/06 is $ 91.06 ; the united parcel service inc . of 12/31/07 is $ 87.88 ; the united parcel service inc . of 12/31/08 is $ 70.48 ; the united parcel service inc . of 12/31/09 is $ 75.95 ;",
            "table_2": "the s&p 500 index of 12/31/04 is $ 100.00 ; the s&p 500 index of 12/31/05 is $ 104.91 ; the s&p 500 index of 12/31/06 is $ 121.48 ; the s&p 500 index of 12/31/07 is $ 128.15 ; the s&p 500 index of 12/31/08 is $ 80.74 ; the s&p 500 index of 12/31/09 is $ 102.11 ;"
        },
        "exe_ans": -0.2616,
        "program_re": "subtract(divide(subtract(75.95, const_100), const_100), divide(subtract(102.11, const_100), const_100))"
    }
}
```

