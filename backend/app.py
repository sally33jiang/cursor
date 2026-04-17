from typing import Dict, List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="MBTI Zodiac Match API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MBTI_TYPES = {
    "ISTJ",
    "ISFJ",
    "INFJ",
    "INTJ",
    "ISTP",
    "ISFP",
    "INFP",
    "INTP",
    "ESTP",
    "ESFP",
    "ENFP",
    "ENTP",
    "ESTJ",
    "ESFJ",
    "ENFJ",
    "ENTJ",
}

ZODIAC_SIGNS = {
    "白羊",
    "金牛",
    "双子",
    "巨蟹",
    "狮子",
    "处女",
    "天秤",
    "天蝎",
    "射手",
    "摩羯",
    "水瓶",
    "双鱼",
}

COLOR_GROUPS: Dict[str, List[str]] = {
    "红人": ["ESTP", "ESFP", "ESTJ", "ESFJ"],
    "黄人": ["ENFP", "ENFJ", "ESFP", "ESTP"],
    "绿人": ["INFP", "INFJ", "ISFP", "ISFJ"],
    "紫人": ["INTJ", "INTP", "ENTP", "ENTJ"],
}

ZODIAC_ELEMENT = {
    "白羊": "火象",
    "狮子": "火象",
    "射手": "火象",
    "金牛": "土象",
    "处女": "土象",
    "摩羯": "土象",
    "双子": "风象",
    "天秤": "风象",
    "水瓶": "风象",
    "巨蟹": "水象",
    "天蝎": "水象",
    "双鱼": "水象",
}

ELEMENT_SIGN = {
    "火象": ["白羊", "狮子", "射手"],
    "土象": ["金牛", "处女", "摩羯"],
    "风象": ["双子", "天秤", "水瓶"],
    "水象": ["巨蟹", "天蝎", "双鱼"],
}

LOVE_RULE = {
    "紫人": {
        "group": "黄人",
        "elements": ["火象", "风象"],
        "reason": "你偏理性独立，黄人更能提供情绪温度与互动活力，火/风象既有趣又尊重边界。",
    },
    "黄人": {
        "group": "紫人",
        "elements": ["水象", "土象"],
        "reason": "你热情感性，紫人能给稳定框架，水/土象提供持续安全感与情绪托底。",
    },
    "绿人": {
        "group": "红人",
        "elements": ["土象", "水象"],
        "reason": "你细腻慢热，红人更主动推进关系，土/水象的包容能让你安心表达。",
    },
    "红人": {
        "group": "绿人",
        "elements": ["火象", "风象"],
        "reason": "你行动派、表达直接，绿人能柔化冲突，火/风象让关系持续有新鲜感。",
    },
}

FRIEND_RULE = {
    "紫人": {
        "group": "紫人",
        "elements": ["风象"],
        "reason": "你们重深度和思维同频，风象沟通轻盈，精神默契高。",
    },
    "黄人": {
        "group": "黄人",
        "elements": ["火象"],
        "reason": "节奏一致、快乐放大，火象能与你形成高能社交搭子。",
    },
    "绿人": {
        "group": "绿人",
        "elements": ["水象"],
        "reason": "彼此细腻共情，水象让情绪承接更稳定、陪伴更治愈。",
    },
    "红人": {
        "group": "红人",
        "elements": ["土象"],
        "reason": "目标一致、执行力强，土象让关系更可靠耐久。",
    },
}

SCORE_DIMENSIONS = ["E", "T", "E", "J", "E", "S", "T", "E", "S", "E", "T", "E", "T", "P", "A", "N"]


class MatchRequest(BaseModel):
    nickname: str = Field(min_length=1)
    birth: str = Field(min_length=1)
    zodiac: str
    mbti: str
    orientation: Literal["恋爱为主", "闺蜜为主", "两者都想要"]
    social: Literal["偏外向", "偏内向", "看情况"]
    answers: List[Literal["A", "B"]] = Field(min_length=16, max_length=16)


def get_color_group(mbti: str) -> str:
    matched = [k for k, v in COLOR_GROUPS.items() if mbti in v]
    if len(matched) <= 1:
        return matched[0] if matched else "未知"
    if "黄人" in matched:
        return "黄人"
    return matched[0]


def score_by_answers(answers: List[str], mbti: str, element: str) -> int:
    base = 68
    extro = 0
    think = 0
    stable = 0
    resonance = 0

    for i, answer in enumerate(answers):
        val = 1 if answer == "A" else -1
        dim = SCORE_DIMENSIONS[i]
        if dim == "E":
            extro += val
        if dim == "T":
            think += val
        if dim in {"J", "S"}:
            stable += val
        if dim in {"A", "N", "P"}:
            resonance += 1 if answer == "B" else 0

    is_e = mbti.startswith("E")
    is_t = "T" in mbti
    stable_bonus = 4 if element in {"土象", "水象"} else 2
    score = base
    score += max(0, 8 - abs(extro - (4 if is_e else -4)))
    score += max(0, 8 - abs(think - (3 if is_t else -3)))
    score += max(0, 8 - abs(stable)) + stable_bonus
    score += min(8, resonance + 2)
    return max(72, min(99, score))


def picks_for_group(group: str) -> List[str]:
    return COLOR_GROUPS.get(group, [])

# 测试路由，解决你直接访问 404 的问题
@app.get("/api/match")
def test_match():
    return {"message": "POST 请求此接口即可获得 MBTI 星座匹配结果"}

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/match")
def generate_match(payload: MatchRequest) -> Dict[str, object]:
    if payload.mbti not in MBTI_TYPES:
        raise HTTPException(status_code=400, detail="无效的 MBTI 类型")
    if payload.zodiac not in ZODIAC_SIGNS:
        raise HTTPException(status_code=400, detail="无效的星座")

    color = get_color_group(payload.mbti)
    if color == "未知":
        raise HTTPException(status_code=400, detail="MBTI 无法映射到色彩分组")

    element = ZODIAC_ELEMENT.get(payload.zodiac, "火象")
    love = LOVE_RULE[color]
    friend = FRIEND_RULE[color]
    love_score = score_by_answers(payload.answers, payload.mbti, element)
    friend_score = min(99, love_score + 4)

    a_count = payload.answers.count("A")
    b_count = 16 - a_count
    keywords = [
        "行动果断" if a_count >= 9 else "感受细腻",
        "精神共鸣" if b_count >= 9 else "现实稳定",
        "社交活跃" if payload.social == "偏外向" else "慢热深度" if payload.social == "偏内向" else "节奏自如",
    ]

    return {
        "profile": {
            "nickname": payload.nickname,
            "birth": payload.birth,
            "zodiac": payload.zodiac,
            "element": element,
            "mbti": payload.mbti,
            "color": color,
            "orientation": payload.orientation,
            "social": payload.social,
        },
        "keywords": keywords,
        "love": {
            "group": love["group"],
            "elements": love["elements"],
            "recommended_zodiac": [sign for e in love["elements"] for sign in ELEMENT_SIGN[e]],
            "recommended_mbti": picks_for_group(love["group"]),
            "reason": love["reason"],
            "score": love_score,
        },
        "friend": {
            "group": friend["group"],
            "elements": friend["elements"],
            "recommended_zodiac": [sign for e in friend["elements"] for sign in ELEMENT_SIGN[e]],
            "recommended_mbti": picks_for_group(friend["group"]),
            "reason": friend["reason"],
            "score": friend_score,
        },
        "insight": {
            "core_need": f"{keywords[1]} + {keywords[2]} 的平衡体验。",
            "risk_point": "当对方节奏过快或过于黏人时，你可能会下意识拉开距离。",
            "why_match": "你擅长提供一种稳定关系底盘，而匹配对象擅长补足你缺失的互动能量。",
            "advice": "明确边界与期待，固定高质量沟通时间，关系会更稳定也更有心动感。",
        },
    }
