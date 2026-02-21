from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class Strategy:
    key: str
    display_name: str                 # "09stop", "game8"
    check_strat_text: str
    tower_texts: List[str]

    text_3_10: Dict[int, str]         # 버튼 3~10 로그 텍스트
    btn_to_mark: Dict[int, str]       # 3~10 -> "Amark" 같은 마크 이미지 키
    check_img_key_map: Dict[int, str] # 3~10 -> "first" 같은 체크 이미지 키

    spread_map_1: Dict[int, str]      # isSpread==1 결과 문자열
    spread_map_2: Dict[int, str]      # isSpread==2 결과 문자열

    # 쉐어 판정
    def is_share(self, n: int) -> bool:
        if self.key == "09stop":
            return 3 <= n <= 6
        if self.key == "game8":
            return n in (3, 8, 9, 10)
        return False

STRATEGIES: Dict[str, Strategy] = {
    "09stop": Strategy(
        key="09stop",
        display_name="09stop",
        check_strat_text="현재 처리법: 09stop",
        tower_texts=[
            "에어로가(공중): 보스정면에 딱 붙기",
            "죽선(빔): 숫자징 뒤쪽 변에 서기",
            "디버프X 원딜: 섬 남쪽(6시) 끝",
            "디버프X 근딜: 숫자징 대상 뒤쪽 붙기",
        ],
        text_3_10={
            3: "숫자 1", 4: "숫자 3", 5: "숫자 2", 6: "숫자 4",
            7: "금지 1", 8: "속박 1", 9: "금지 2", 10:"속박 2",
        },
        btn_to_mark={
            3: "Amark", 7: "Amark",
            4: "Bmark", 8: "Bmark",
            5: "Cmark", 9: "Cmark",
            6: "Dmark", 10:"Dmark",
        },
        check_img_key_map={
            3:"first", 4:"third", 5:"second", 6:"fourth",
            7:"stop1", 8:"bind1", 9:"stop2", 10:"bind2",
        },
        spread_map_1={
            3:"center - 1 - center - 1",
            4:"center - 1 - center - 1",
            5:"center - 2 - center - 2",
            6:"center - 2 - center - 2",
            7:"D - 1 - center - 1",
            8:"center - 1 - D - 1",
            9:"C - 2 - center - 2",
            10:"center - 2 - C - 2",
        },
        spread_map_2={
            3:"1 - center - 1 - center",
            4:"1 - center - 1 - center",
            5:"2 - center - 2 - center",
            6:"2 - center - 2 - center",
            7:"1 - D - 1 - center",
            8:"1 - center - 1 - D",
            9:"2 - C - 2 - center",
            10:"2 - center - 2 - C",
        },
    ),

    "game8": Strategy(
        key="game8",
        display_name="Game8",
        check_strat_text="현재 처리법: Game8",
        tower_texts=[
            "에어로가(공중): 남쪽 타겟서클 위",
            "죽선(빔): 남쪽 숫자징 모서리 서기",
            "디버프X 원딜: 섬 북쪽(12시) 끝",
            "디버프X 근딜: 숫자징 대상 남쪽 붙기",
        ],
        text_3_10={
            3:"숫자 4", 4:"숫자 1", 5:"금지 2", 6:"숫자 2",
            7:"금지 1", 8:"속박 1", 9:"속박 2", 10:"숫자 3",
        },
        btn_to_mark={
            3:"Amark", 7:"Cmark",
            4:"Amark", 8:"Cmark",
            5:"Dmark", 9:"Dmark",
            6:"Bmark", 10:"Bmark",
        },
        check_img_key_map={
            3:"fourth", 4:"first", 5:"stop2", 6:"second",
            7:"stop1", 8:"bind1", 9:"bind2", 10:"third",
        },
        spread_map_1={
            3:"center - 3 - center - 3",
            4:"2 - 3 - center - 3",
            5:"center - 4 - 1 - 4",
            6:"center - 3 - 2 - 3",
            7:"1 - 4 - center - 4",
            8:"center - 4 - center - 4",
            9:"center - 4 - center - 4",
            10:"center - 3 - center - 3",
        },
        spread_map_2={
            3:"3 - center - 3 - center",
            4:"3 - 2 - 3 - center",
            5:"4 - center - 4 - 1",
            6:"3 - center - 3 - 2",
            7:"4 - 1 - 4 - center",
            8:"4 - center - 4 - center",
            9:"4 - center - 4 - center",
            10:"3 - center - 3 - center",
        },
    ),
}