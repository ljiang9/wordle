#!/usr/bin/env python3
"""wordle —— 终端 Wordle 小游戏。

玩法：6 次机会猜出一个 5 字母英文单词。
反馈：🟩 字母和位置都对；🟨 字母在单词里但位置不对；⬛ 字母不在单词里。
纯标准库，离线可玩。
"""

import argparse
import random
import sys
from datetime import date

WORDS = [
    "slate", "crane", "adieu", "about", "above",
    "abuse", "actor", "acute", "admit", "adopt",
    "adult", "after", "again", "agent", "agree",
    "ahead", "alarm", "album", "alert", "alike",
    "alive", "allow", "alone", "along", "aloud",
    "alter", "among", "anger", "angle", "angry",
    "apart", "apple", "apply", "arena", "argue",
    "arise", "array", "aside", "asset", "audio",
    "audit", "avoid", "awake", "award", "aware",
    "awful", "bacon", "badge", "badly", "baker",
    "beach", "beard", "beast", "begin", "belly",
    "below", "bench", "berry", "birth", "black",
    "blade", "blame", "blank", "blast", "blend",
    "bless", "blind", "block", "blood", "bloom",
    "board", "boast", "bonus", "booth", "bound",
    "brain", "brand", "brave", "bread", "break",
    "brick", "brief", "bring", "broad", "broke",
    "brown", "brush", "build", "bunch", "buyer",
    "cabin", "cable", "canal", "candy", "carry",
    "catch", "cause", "cease", "chain", "chair",
    "chaos", "charm", "chart", "chase", "cheap",
    "check", "chest", "chief", "child", "chill",
    "choir", "chunk", "civil", "claim", "class",
    "clean", "clear", "clerk", "click", "cliff",
    "climb", "clock", "clone", "close", "cloth",
    "cloud", "clown", "coach", "coast", "cobra",
    "cocoa", "colon", "color", "comet", "comma",
    "comic", "conch", "coral", "could", "count",
    "court", "cover", "crack", "craft", "crash",
    "crazy", "cream", "crime", "crisp", "cross",
    "crowd", "crown", "crude", "crush", "curve",
    "cycle", "dance", "death", "delay", "depth",
    "diary", "dirty", "dodge", "doing", "doubt",
    "dozen", "draft", "drain", "drama", "dream",
    "dress", "drink", "drive", "eager", "early",
    "earth", "eight", "elbow", "elder", "elect",
    "elite", "empty", "enemy", "enjoy", "enter",
    "entry", "equal", "error", "essay", "event",
    "every", "exact", "exist", "extra", "faint",
    "faith", "false", "fancy", "fatal", "favor",
]

WORD_SET = set(WORDS)
WORD_LEN = 5
MAX_TRIES = 6

_EMOJI = {"green": "🟩", "yellow": "🟨", "black": "⬛"}
_KB_RANK = {"black": 1, "yellow": 2, "green": 3}


def score_guess(guess, answer):
    """标准 Wordle 评分：先标绿，再按剩余字母数量标黄。

    guess / answer 均为小写 5 字母字符串。
    返回长度为 5 的状态列表，元素为 green / yellow / black。
    """
    result = ["black"] * WORD_LEN
    remaining = {}
    for i in range(WORD_LEN):
        if guess[i] == answer[i]:
            result[i] = "green"
        else:
            remaining[answer[i]] = remaining.get(answer[i], 0) + 1
    for i in range(WORD_LEN):
        if result[i] == "black":
            ch = guess[i]
            if remaining.get(ch, 0) > 0:
                result[i] = "yellow"
                remaining[ch] -= 1
    return result


def render_states(states):
    """把状态列表渲染成 🟩🟨⬛ 字符串。"""
    return "".join(_EMOJI[s] for s in states)


def update_keyboard(kb, guess, states):
    """更新键盘提示：每个字母只保留最高状态（绿 > 黄 > 灰）。"""
    for ch, st in zip(guess, states):
        if _KB_RANK[st] > _KB_RANK.get(ch, 0):
            kb[ch] = st


def render_keyboard(kb, out):
    """打印 QWERTY 键盘提示（ANSI 底色：绿=确定，黄=在词中，灰=排除）。"""
    for row in ("qwertyuiop", "asdfghjkl", "zxcvbnm"):
        cells = []
        for ch in row:
            st = kb.get(ch)
            label = ch.upper()
            if st == "green":
                cells.append("\033[42m\033[30m " + label + " \033[0m")
            elif st == "yellow":
                cells.append("\033[43m\033[30m " + label + " \033[0m")
            elif st == "black":
                cells.append("\033[100m\033[30m " + label + " \033[0m")
            else:
                cells.append(" " + label + " ")
        out(" ".join(cells))


def daily_word(today=None):
    """按日期确定的每日单词：同一天玩到的是同一个词。"""
    day = today or date.today().isoformat()
    return random.Random("wordle:" + day).choice(WORDS)


def play(answer, read_guess, out):
    """玩一局。read_guess(prompt) 读取一次猜测，遇到 EOF 时抛 EOFError。

    返回 True（猜中）/ False（失败）。
    """
    kb = {}
    for attempt in range(1, MAX_TRIES + 1):
        while True:
            try:
                raw = read_guess("第 %d/%d 次猜测： " % (attempt, MAX_TRIES))
            except EOFError:
                out("")
                out("输入结束，游戏结束。答案是：" + answer.upper())
                return False
            guess = raw.strip().lower()
            if len(guess) != WORD_LEN or not guess.isalpha():
                out("请输入 %d 个英文字母。" % WORD_LEN)
                continue
            if guess not in WORD_SET:
                out("词库里没有这个词，换一个试试。")
                continue
            break
        states = score_guess(guess, answer)
        out("  %s  %s" % (guess.upper(), render_states(states)))
        update_keyboard(kb, guess, states)
        render_keyboard(kb, out)
        if all(s == "green" for s in states):
            out("🎉 猜中了！共用了 %d 次。答案：%s" % (attempt, answer.upper()))
            return True
    out("😅 6 次机会用完了。答案是：" + answer.upper())
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="wordle",
        description="终端 Wordle：6 次机会猜一个 5 字母英文单词。",
    )
    parser.add_argument("--word", metavar="WORD",
                        help="固定答案（测试/演示用），如 --word CRANE")
    parser.add_argument("--daily", action="store_true",
                        help="每日一词：按日期确定答案，同一天答案相同")
    parser.add_argument("--auto", nargs="?", const="", metavar="GUESSES",
                        help="自动演示：逗号分隔的猜测序列，如 --auto slate,crane；"
                             "不带参数时用内置演示序列")
    args = parser.parse_args(argv)

    if args.word:
        answer = args.word.strip().lower()
        if len(answer) != WORD_LEN or not answer.isalpha() or answer not in WORD_SET:
            print("error: --word 必须是词库中的 %d 字母单词" % WORD_LEN,
                  file=sys.stderr)
            return 2
    elif args.daily:
        answer = daily_word()
    else:
        answer = random.choice(WORDS)

    if args.auto is not None:
        if args.auto:
            seq = [g.strip().lower() for g in args.auto.split(",")]
        elif answer == "crane":
            seq = ["slate", "crane"]
        else:
            seq = ["adieu", answer]
        seq = [g for g in seq if g]
        it = iter(seq)

        def read_guess(prompt=""):
            try:
                g = next(it)
            except StopIteration:
                raise EOFError
            print(prompt + g)
            return g

        won = play(answer, read_guess, print)
    else:
        won = play(answer, input, print)
    return 0 if won else 1


if __name__ == "__main__":
    sys.exit(main())
