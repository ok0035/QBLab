#!/usr/bin/env python3
"""큐비랩 데일리 브리핑 대시보드 이미지 생성

Usage:
    python generate_dashboard.py --date "2026. 03. 24" --price "$70,800" \
        --change "+4.4%" --position LONG --fear-greed 28 \
        --output static/images/posts/260324-dashboard.png
"""

import argparse
import os
import re
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties

plt.rcParams['axes.unicode_minus'] = False


def _normalize_change(raw: str) -> tuple[str, bool]:
    """변동률 입력을 정규화한다.

    허용 입력: "+4.4%", "-2.5%", "+4.4", "-2.5", "up4.4", "down2.5" 등
    반환: (표시 문자열 예: "+4.4%", 상승 여부 bool)
    """
    s = raw.strip().lstrip("\\")

    # "up/down" 접두어 → 부호로 변환
    m = re.match(r'(?i)(up|down)\s*([0-9.]+)\s*(%)?$', s)
    if m:
        sign = '+' if m.group(1).lower() == 'up' else '-'
        num = m.group(2)
        return f"{sign}{num}%", sign == '+'

    # "+/-" 부호 시작
    m = re.match(r'([+-])\s*([0-9.]+)\s*(%)?$', s)
    if m:
        sign = m.group(1)
        num = m.group(2)
        return f"{sign}{num}%", sign == '+'

    # 부호 없이 숫자만 (예: "4.4%", "2.5")
    m = re.match(r'([0-9.]+)\s*(%)?$', s)
    if m:
        num = m.group(1)
        return f"+{num}%", True

    print(f"오류: 변동률 형식을 인식할 수 없습니다: '{raw}'", file=sys.stderr)
    print("  허용 형식: '+4.4%', '-2.5%', 'up4.4', 'down2.5'", file=sys.stderr)
    sys.exit(1)


def generate_dashboard(date_str, btc_price, btc_change, position, fear_greed, output_path):
    # === 폰트 ===
    fp_bold = FontProperties(family='Pretendard', weight='bold')
    fp_semi = FontProperties(family='Pretendard', weight='semibold')
    fp_medium = FontProperties(family='Pretendard', weight='medium')
    fp_regular = FontProperties(family='Pretendard', weight='regular')

    # === 파생 값 ===
    btc_change, btc_change_positive = _normalize_change(btc_change)
    pos_upper = position.upper()
    is_long = pos_upper in ("LONG", "롱", "롱 매수")
    is_short = pos_upper in ("SHORT", "숏", "숏 매수")

    if is_long:
        pos_label = "LONG"
        pos_positive = True
    elif is_short:
        pos_label = "SHORT"
        pos_positive = False
    else:
        pos_label = "NEUTRAL"
        pos_positive = None

    # === 색상 ===
    BG = "#FFFFFF"
    TEXT_BLACK = "#1E1F21"
    TEXT_MUTED = "#9999A1"
    BORDER = "#E6E6E9"
    GREEN = "#10B981"
    RED = "#EF4444"
    NEUTRAL_COLOR = "#6B7280"

    # === 캔버스 ===
    fig = plt.figure(figsize=(12, 6.3), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.3)
    ax.set_facecolor(BG)
    ax.axis('off')

    # --- 외곽 ---
    outer = FancyBboxPatch(
        (0.15, 0.15), 11.7, 6.0,
        boxstyle="round,pad=0.15",
        facecolor=BG,
        edgecolor=BORDER,
        linewidth=1.2
    )
    ax.add_patch(outer)

    # 날짜
    ax.text(0.7, 5.5, date_str, fontsize=14, color=TEXT_MUTED,
            fontproperties=fp_regular, va='center')

    # BTC 가격
    ax.text(6.0, 3.9, btc_price, fontsize=72, color=TEXT_BLACK,
            fontproperties=fp_bold, ha='center', va='center')

    # 변동률
    change_color = GREEN if btc_change_positive else RED
    arrow = "▲" if btc_change_positive else "▼"
    ax.text(6.0, 2.8, f"{arrow} {btc_change}", fontsize=28,
            color=change_color, fontproperties=fp_semi,
            ha='center', va='center')

    # 구분선
    ax.plot([0.7, 11.3], [1.7, 1.7], color=BORDER, linewidth=1)

    # 포지션
    if pos_positive is True:
        pos_color = GREEN
    elif pos_positive is False:
        pos_color = RED
    else:
        pos_color = NEUTRAL_COLOR

    ax.text(3.5, 1.1, "POSITION", fontsize=13, color=TEXT_MUTED,
            fontproperties=fp_medium, ha='center', va='center')
    ax.text(3.5, 0.55, pos_label, fontsize=24, color=pos_color,
            fontproperties=fp_bold, ha='center', va='center')

    # 세로 구분선
    ax.plot([6.0, 6.0], [0.4, 1.5], color=BORDER, linewidth=1)

    # 공포지수
    ax.text(8.5, 1.1, "FEAR & GREED", fontsize=13, color=TEXT_MUTED,
            fontproperties=fp_medium, ha='center', va='center')
    ax.text(8.5, 0.55, str(fear_greed), fontsize=24, color=TEXT_BLACK,
            fontproperties=fp_bold, ha='center', va='center')

    # 워터마크
    ax.text(11.3, 5.5, "qblab.kr", fontsize=12, color=TEXT_MUTED,
            fontproperties=fp_regular, ha='right', va='center')

    # 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                pad_inches=0, facecolor=BG)
    plt.close()
    print(f"저장 완료: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="큐비랩 대시보드 이미지 생성")
    parser.add_argument("--date", required=True, help="날짜 (예: '2026. 03. 24')")
    parser.add_argument("--price", required=True, help="BTC 가격 (예: '$70,800')")
    parser.add_argument("--change", required=True, help="변동률 (예: '+4.4%%')")
    parser.add_argument("--position", required=True, help="포지션 (LONG/SHORT/NEUTRAL)")
    parser.add_argument("--fear-greed", type=int, required=True, help="공포탐욕지수 (0-100)")
    parser.add_argument("--output", required=True, help="출력 파일 경로")

    args = parser.parse_args()
    generate_dashboard(args.date, args.price, args.change,
                       args.position, args.fear_greed, args.output)
