import argparse
import sys

from service import add_room, add_bed, checkin, checkout, overdue, monthly, VALID_ROOM_TYPES_LIST


def main():
    parser = argparse.ArgumentParser(description="青年旅舍管理系统")
    subparsers = parser.add_subparsers(dest="command")

    p_room = subparsers.add_parser("add-room", help="添加房间")
    p_room.add_argument("room_id", help="房间编号")
    p_room.add_argument("name", help="房间名称")
    p_room.add_argument("--type", required=True, dest="room_type", choices=VALID_ROOM_TYPES_LIST, help="房间类型：6人间/8人间/4人间/双人间")
    p_room.add_argument("--beds", required=True, type=int, help="床位数")

    p_bed = subparsers.add_parser("add-bed", help="添加床位")
    p_bed.add_argument("room_id", help="房间编号")
    p_bed.add_argument("bed_id", help="床位编号")

    p_checkin = subparsers.add_parser("checkin", help="入住")
    p_checkin.add_argument("bed_id", help="床位编号")
    p_checkin.add_argument("--guest", required=True, help="客人姓名")
    p_checkin.add_argument("--phone", required=True, help="联系电话")
    p_checkin.add_argument("--nights", required=True, help="入住晚数")
    p_checkin.add_argument("--date", required=True, help="入住日期 YYYY-MM-DD")

    p_checkout = subparsers.add_parser("checkout", help="退房")
    p_checkout.add_argument("bed_id", help="床位编号")

    subparsers.add_parser("overdue", help="超期未退房记录")

    p_monthly = subparsers.add_parser("monthly", help="月度统计")
    p_monthly.add_argument("--month", required=True, help="月份 YYYY-MM")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "add-room": lambda: add_room(args.room_id, args.name, args.room_type, args.beds),
        "add-bed": lambda: add_bed(args.room_id, args.bed_id),
        "checkin": lambda: checkin(args.bed_id, args.guest, args.phone, args.nights, args.date),
        "checkout": lambda: checkout(args.bed_id),
        "overdue": lambda: overdue(),
        "monthly": lambda: monthly(args.month),
    }

    dispatch[args.command]()


if __name__ == "__main__":
    main()
