from datetime import date, timedelta

from storage import load, save

VALID_ROOM_TYPES = {"6人间", "8人间", "4人间", "双人间"}

PRICE_PER_NIGHT = 50


def add_room(room_id, name, room_type, beds):
    if room_type not in VALID_ROOM_TYPES:
        print(f"错误：房间类型只能是 {', '.join(sorted(VALID_ROOM_TYPES))}")
        return
    data = load()
    if room_id in data["rooms"]:
        print(f"错误：房间 {room_id} 已存在")
        return
    data["rooms"][room_id] = {
        "name": name,
        "type": room_type,
        "beds_count": beds,
    }
    save(data)
    print(f"房间 {room_id}（{name}，{room_type}，{beds}个床位）添加成功")


def add_bed(room_id, bed_id):
    data = load()
    if room_id not in data["rooms"]:
        print(f"错误：房间 {room_id} 不存在")
        return
    if bed_id in data["beds"]:
        print(f"错误：床位 {bed_id} 已存在")
        return
    data["beds"][bed_id] = {
        "room_id": room_id,
        "status": "空闲",
    }
    save(data)
    print(f"床位 {bed_id}（房间 {room_id}）添加成功，状态：空闲")


def checkin(bed_id, guest, phone, nights, checkin_date_str):
    try:
        nights_int = int(nights)
    except (ValueError, TypeError):
        print("错误：nights 必须是正整数")
        return
    if nights_int <= 0:
        print("错误：nights 必须是正整数")
        return

    try:
        checkin_date = date.fromisoformat(checkin_date_str)
    except (ValueError, TypeError):
        print("错误：日期格式无效，请使用 YYYY-MM-DD")
        return

    data = load()
    if bed_id not in data["beds"]:
        print(f"错误：床位 {bed_id} 不存在")
        return
    if data["beds"][bed_id]["status"] != "空闲":
        print(f"错误：床位 {bed_id} 当前状态为 {data['beds'][bed_id]['status']}，无法入住")
        return

    expected_checkout = checkin_date + timedelta(days=nights_int)

    data["beds"][bed_id]["status"] = "占用"
    record = {
        "bed_id": bed_id,
        "room_id": data["beds"][bed_id]["room_id"],
        "guest": guest,
        "phone": phone,
        "nights": nights_int,
        "checkin_date": checkin_date_str,
        "expected_checkout": expected_checkout.isoformat(),
        "actual_checkout": None,
        "fee": None,
    }
    data["checkins"].append(record)
    save(data)
    print(f"入住成功：{guest} 入住床位 {bed_id}，{nights_int}晚，预计离店 {expected_checkout.isoformat()}")


def checkout(bed_id):
    data = load()
    if bed_id not in data["beds"]:
        print(f"错误：床位 {bed_id} 不存在")
        return
    if data["beds"][bed_id]["status"] != "占用":
        print(f"错误：床位 {bed_id} 当前未入住，无法退房")
        return

    record = None
    for r in reversed(data["checkins"]):
        if r["bed_id"] == bed_id and r["actual_checkout"] is None:
            record = r
            break

    if record is None:
        print(f"错误：未找到床位 {bed_id} 的在住记录")
        return

    fee = record["nights"] * PRICE_PER_NIGHT
    today = date.today().isoformat()

    record["actual_checkout"] = today
    record["fee"] = fee
    data["beds"][bed_id]["status"] = "空闲"

    save(data)
    print(f"退房成功：{record['guest']} 从床位 {bed_id} 退房，住宿费 {fee} 元")


def overdue():
    data = load()
    today = date.today()
    results = []
    for r in data["checkins"]:
        if r["actual_checkout"] is not None:
            continue
        expected = date.fromisoformat(r["expected_checkout"])
        if today > expected:
            overdue_days = (today - expected).days
            results.append((r, overdue_days))

    if not results:
        print("当前无超期未退房记录")
        return

    print(f"{'床位':<8} {'客人':<10} {'入住日期':<14} {'预计离店':<14} {'超期天数':<8}")
    print("-" * 60)
    for r, days in results:
        print(f"{r['bed_id']:<8} {r['guest']:<10} {r['checkin_date']:<14} {r['expected_checkout']:<14} {days:<8}")


def monthly(month_str):
    try:
        year, month = month_str.split("-")
        year = int(year)
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError
    except (ValueError, TypeError):
        print("错误：月份格式无效，请使用 YYYY-MM")
        return

    data = load()
    target_prefix = f"{year:04d}-{month:02d}"

    room_type_stats = {}
    for r in data["checkins"]:
        checkin_month = r["checkin_date"][:7]
        if checkin_month != target_prefix:
            continue
        room_id = r["room_id"]
        room_info = data["rooms"].get(room_id, {})
        rtype = room_info.get("type", "未知")

        if rtype not in room_type_stats:
            room_type_stats[rtype] = {"count": 0, "income": 0}
        room_type_stats[rtype]["count"] += 1
        if r["fee"] is not None:
            room_type_stats[rtype]["income"] += r["fee"]

    if not room_type_stats:
        print(f"{month_str} 无入住记录")
        return

    print(f"{'房间类型':<10} {'入住人次':<10} {'收入（元）':<10}")
    print("-" * 35)
    for rtype in sorted(room_type_stats.keys()):
        stats = room_type_stats[rtype]
        print(f"{rtype:<10} {stats['count']:<10} {stats['income']:<10}")
