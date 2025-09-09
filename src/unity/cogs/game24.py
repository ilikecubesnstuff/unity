import logging
import random
import time
from itertools import permutations

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class Game24(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = set()

        with open("data/game24/4d12.txt") as f:
            self.solvable = [
                tuple(map(int, line.strip().split()))
                for line in f.readlines()
                if line.strip()
            ]

    def sample(self):
        return random.choice(list(permutations(random.choice(self.solvable))))

    twentyfour = discord.SlashCommandGroup("twentyfour", "Play the 24 game")

    @twentyfour.command(name="start")
    @discord.option(
        "timeout",
        int,
        description="Time limit in minutes (default 5)",
        required=False,
        default=5,
    )
    async def start_game(self, ctx, timeout: int):
        """Start a new game of 24."""
        if ctx.channel.id in self.games:
            await ctx.respond("A game is already running in this channel.")
            return
        self.games.add(ctx.channel.id)

        await ctx.respond("Starting a new game of 24!")
        while True:
            nums = self.sample()
            start_time = time.time()
            prompt = await ctx.send(", ".join(map(str, nums)))
            try:
                answer = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.channel == ctx.channel
                    and self.eval_check(m.content, nums),
                    timeout=timeout * 60,
                )
            except TimeoutError:
                self.games.remove(ctx.channel.id)
                await prompt.edit(
                    content=", ".join(map(str, nums))
                    + "\n-# Time's up! No correct answer was given."
                )
                await ctx.send("24 game ended due to timeout.")
                return

            if answer.content.lower() in ["quit", "exit", "stop"]:
                self.games.remove(ctx.channel.id)
                await prompt.edit(
                    content=", ".join(map(str, nums)) + "\n-# Game ended."
                )
                await ctx.send(f"24 game ended by {answer.author.mention}.")
                return
            elapsed = time.time() - start_time
            await prompt.edit(
                content=", ".join(map(str, nums))
                + f"\n-# {answer.author.mention} got it in {elapsed:.2f} seconds with `{answer.content}`."
            )

    def eval_check(self, expr, nums, target=24):
        if expr.lower() in ["quit", "exit", "stop"]:
            return True
        try:
            tokens = tokenize(expr)
        except Exception:
            return False

        inums = extract_nums(tokens)
        if sorted(inums) != sorted(nums):
            return False

        result = self.eval_expr(expr)
        return result == target

    def eval_expr(self, expr):
        try:
            tokens = tokenize(expr)
        except Exception:
            pass
        try:
            return eval_infix(tokens)
        except Exception:
            pass
        try:
            return eval_postfix(tokens)
        except Exception:
            pass
        try:
            return eval_prefix(tokens)
        except Exception:
            pass


def tokenize(text):
    tokens = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in "0123456789":
            buffer = char
            while i + 1 < len(text) and text[i + 1] in "0123456789":
                i += 1
                buffer += text[i]
            tokens.append(int(buffer))
        elif char in "+-*/":
            tokens.append(char)
        elif char in '(':
            j = i
            depth = 1
            while depth > 0:
                j += 1
                if text[j] == '(':
                    depth += 1
                elif text[j] == ')':
                    depth -= 1
            tokens.append(tokenize(text[i + 1:j]))
            i = j
        elif char in " ":
            pass
        else:
            raise ValueError(f"Invalid character in expression: {char}")
        i += 1
    return tokens


def extract_nums(tokens):
    print("extracting nums from", tokens)
    nums = []
    for t in tokens:
        if isinstance(t, list):
            nums.extend(extract_nums(t))
        elif isinstance(t, (int, float)):
            nums.append(t)
    return nums


def eval_prefix(tokens):
    def helper(tokens):
        token = tokens.pop(0)
        if isinstance(token, list):
            return helper(token)
        if isinstance(token, (int, float)):
            return token
        a = helper(tokens)
        b = helper(tokens)
        if token == "+":
            return a + b
        elif token == "-":
            return a - b
        elif token == "*":
            return a * b
        elif token == "/":
            if b == 0:
                raise ZeroDivisionError("division by zero")
            return a / b
        else:
            raise ValueError(f"Invalid operator: {token}")

    return helper(tokens)


def eval_infix(tokens):
    tokens = [t if not isinstance(t, list) else eval_infix(t) for t in tokens]

    # division pass
    while "/" in tokens:
        i = tokens.index("/")
        a = tokens[i - 1]
        b = tokens[i + 1]
        if b == 0:
            raise ZeroDivisionError("division by zero")
        tokens = tokens[: i - 1] + [a / b] + tokens[i + 2 :]

    # multiplication pass
    while "*" in tokens:
        i = tokens.index("*")
        a = tokens[i - 1]
        b = tokens[i + 1]
        tokens = tokens[: i - 1] + [a * b] + tokens[i + 2 :]

    # addition and subtraction pass
    while len(tokens) > 1:
        a, op, b, *rest = tokens
        if op == "+":
            tokens = [a + b] + rest
        elif op == "-":
            tokens = [a - b] + rest
        else:
            raise ValueError(f"Invalid operator in addition/subtraction pass: {op}")
    return tokens[0]


def eval_postfix(tokens):
    stack = []
    for token in tokens:
        if isinstance(token, (int, float)):
            stack.append(token)
        elif token in "+-*/":
            b = stack.pop()
            a = stack.pop()
            if token == "+":
                stack.append(a + b)
            elif token == "-":
                stack.append(a - b)
            elif token == "*":
                stack.append(a * b)
            elif token == "/":
                if b == 0:
                    raise ZeroDivisionError("division by zero")
                stack.append(a / b)
            else:
                raise ValueError(f"Invalid operator in postfix expression: {token}")
    if len(stack) != 1:
        raise ValueError("Invalid postfix expression")
    return stack[0]


def setup(bot):
    bot.add_cog(Game24(bot))
