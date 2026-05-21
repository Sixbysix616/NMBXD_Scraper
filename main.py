"""CLI entry point for the nmbxd thread scraper."""
import re

from nmbxd_scraper import fetch_thread


def main():
    tid = input("请输入串号：\n> ").strip()
    if not re.match(r"^\d+$", tid):
        print("❌ 无效串号，请输入纯数字")
        raise SystemExit(1)

    print("\n请选择保存格式：")
    print("1. 仅保存 TXT")
    print("2. 仅保存 HTML")
    print("3. 同时保存 TXT 和 HTML")

    mode = input("> ").strip()
    if mode not in {"1", "2", "3"}:
        print("❌ 无效选择，默认保存 TXT")
        mode = "1"

    fetch_thread(tid, save_txt=(mode in {"1", "3"}), save_html=(mode in {"2", "3"}))


if __name__ == "__main__":
    main()
