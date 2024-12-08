import random
import hashlib
from dates import zodiac_sign_dates

cache = {}


def get_horoscope_by_birthday(birth_month: int, birth_day: int):

    # 以生日為主產生固定的隨機數
    seed_day = f"{birth_month}/{birth_day}"
    random.seed(hashlib.md5(seed_day.encode("utf-8")).hexdigest())

    career_coss = random.randint(1, 10)
    love_coss = random.randint(1, 10)
    wealth_coss = random.randint(1, 10)

    # 設定占卜分數
    point = {
        1: "大凶",
        2: "大凶",
        3: "凶",
        4: "凶",
        5: "良好",
        6: "良好",
        7: "優良",
        8: "優良",
        9: "大吉",
        10: "大吉",
    }

    # 輸出占卜結果
    career = point[career_coss]  # 事業運勢
    love = point[love_coss]  # 感情運勢
    wealth = point[wealth_coss]  # 財運運勢

    total_coss = (career_coss + love_coss + wealth_coss) // 3  # 占卜總分與評價

    if total_coss <= 3:
        total_point = "您今天的運勢是很差的，一言難盡。"
    elif total_coss <= 7:
        total_point = "您今天的運勢是良好，可保持平常心。"
    else:
        total_point = "您今天的運勢超棒的，無所畏懼！勇往直前！！！"

    # 輸出占卜結果
    return {
        "career_coss": career_coss,
        "love_coss": love_coss,
        "wealth_coss": wealth_coss,
        "career": career,
        "love": love,
        "wealth": wealth,
        "total_coss": total_coss,
        "total_point": total_point,
    }


def get_results(birth_month: int, birth_day: int) -> str:
    user_zodiac = None

    # 星座識別邏輯
    for zodiac, (start, end) in zodiac_sign_dates.items():
        start_month, start_day = start
        end_month, end_day = end

        # 處理跨年星座邏輯
        if (birth_month == start_month and birth_day >= start_day) or (
            birth_month == end_month and birth_day <= end_day
        ):
            user_zodiac = zodiac
            break

    if user_zodiac:

        # 檢查該user_id是否有存儲過運勢結果
        birthday = (birth_month, birth_day)

        # 若無則計算結果存入快取
        if birthday not in cache:
            cache[birthday] = get_horoscope_by_birthday(birth_month, birth_day)

        # 從快取中取出運勢結果
        horoscope = cache[birthday]

        return (
            f"您的星座是: {user_zodiac}\n"
            f"事業運勢: {horoscope['career_coss']}分-{horoscope['career']}\n"
            f"感情運勢: {horoscope['love_coss']}分-{horoscope['love']}\n"
            f"財運運勢: {horoscope['wealth_coss']}分-{horoscope['wealth']}\n"
            f"今天總體運勢: {horoscope['total_point']}"
        )

    else:
        print("Zodiac not found")
        return "您輸入的日期無法識別星座，請檢查日期"
