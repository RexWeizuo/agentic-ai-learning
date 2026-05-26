---
title: 类型三：求幂指型（$1^\infty, \infty^0, 0^0$）未定式的极限
date: 2026-05-17T00:00:00+08:00
lastmod: 2026-05-19T10:54:03+08:00
---

# 类型三：求幂指型（$1^\infty, \infty^0, 0^0$）未定式的极限

```
``````

## 类型三：求幂指型（$1^\infty, \infty^0, 0^0$）未定式的极限

### 【解题方法】

遇到 $1^\infty, \infty^0, 0^0$ 型未定式的极限，根据 $\lim f(x)^{g(x)} = e^{\lim g(x) \ln f(x)}$ 可转化为求 $\lim g(x) \ln f(x)$ 的极限，而 $g(x) \ln f(x)$ 必定为 $0 \cdot \infty$ 型未定式，因此可再化为 $\frac{0}{0}$ 型或 $\frac{\infty}{\infty}$ 型未定式的极限计算.

### 【例 1.12】求极限 $\lim_{x \to 0} \left[ \frac{\ln(1+x)}{x} \right]^{\frac{1}{e^x-1}}$

转换后 + 泰勒可做

![image](assets/image-20260519104528-3ehqfa3.png)

### 【例 1.13】求极限 $\lim_{x \to +\infty} (x+e^x)^{\frac{1}{x}}$

![image](assets/image-20260519104551-bc2xhw5.png)

### 【例 1.14】求极限 $\lim_{x \to +\infty} \left( x^{\frac{1}{x}} - 1 \right)^{\frac{1}{\ln x}}$

复合函数内部等价无穷小有条件 直接洛必达细心计算也行

![image](assets/image-20260519104609-25c8s4t.png)

### 【例 1.15】求极限 $\lim_{x \to \infty} \left[ \frac{x^{1+x}}{(1+x)^x} - \frac{x}{e} \right]$

能不能看出 提出一个x

![image](assets/image-20260519105126-fqwo7td.png)

这份文档处理的是**幂指型未定式**：$1^\infty$、$\infty^0$、$0^0$。核心思想就一句话：**取对数，变指数为乘积，再化为** **$\frac{0}{0}$** **或** **$\frac{\infty}{\infty}$** **求解**。

---

## 一、整体思路与转化链

形如

$$
\lim f(x)^{g(x)}
$$

的未定式，**固定套路**：

1. 写为

   $$
   f(x)^{g(x)} = e^{g(x)\ln f(x)}
   $$
2. 令 $A = \lim g(x)\ln f(x)$，则原式 $= e^A$。
3. $g(x)\ln f(x)$ 必定是 **$0\cdot\infty$** 型（对照类型二的转化方法）。
4. 化为 $\frac{0}{0}$ 或 $\frac{\infty}{\infty}$，再用等价替换、泰勒或洛必达求 $A$。

**各类型典型表现**：

- **$1^\infty$**：$f(x)\to1$，$\ln f(x)\to0$，$g(x)\to\infty$，乘积 $0\cdot\infty$。
- **$\infty^0$**：$f(x)\to\infty$，$\ln f(x)\to\infty$，$g(x)\to0$，乘积 $0\cdot\infty$。
- **$0^0$**：$f(x)\to0^+$，$\ln f(x)\to-\infty$，$g(x)\to0$，乘积 $0\cdot\infty$。

---

## 二、例题详解

### 【例 1.12】

$$
\lim_{x \to 0} \left[ \frac{\ln(1+x)}{x} \right]^{\frac{1}{e^x-1}}
$$

**分析**：  
$x\to0$ 时，$\frac{\ln(1+x)}{x} \to 1$，指数 $\frac{1}{e^x-1}\to\infty$，属于 **$1^\infty$** **型**。

**解**：

令

$$
L = \lim_{x\to0} \frac{1}{e^x-1} \cdot \ln\left(\frac{\ln(1+x)}{x}\right)
$$

则原式 $= e^L$。  
分母 $e^x-1\sim x$。

分子考虑 $\ln\left(\frac{\ln(1+x)}{x}\right)$，先将 $\ln(1+x)$ 展开：

$$
\ln(1+x) = x - \frac{x^2}{2} + \frac{x^3}{3} - \frac{x^4}{4} + o(x^4)
$$

$$
\frac{\ln(1+x)}{x} = 1 - \frac{x}{2} + \frac{x^2}{3} - \frac{x^3}{4} + o(x^3)
$$

再求对数：利用 $\ln(1+u) = u - \frac{u^2}{2} + \frac{u^3}{3} - \cdots$，其中 $u = -\frac{x}{2} + \frac{x^2}{3} - \frac{x^3}{4} + o(x^3)$。

$$
\begin{aligned}
\ln\left( \frac{\ln(1+x)}{x} \right) 
&= \ln\left(1 - \frac{x}{2} + \frac{x^2}{3} - \frac{x^3}{4} + o(x^3)\right) \\
&= \left(-\frac{x}{2} + \frac{x^2}{3} - \frac{x^3}{4}\right) 
- \frac{1}{2}\left(-\frac{x}{2} + \frac{x^2}{3}\right)^2 
+ \frac{1}{3}\left(-\frac{x}{2}\right)^3 + o(x^3) \\
&= -\frac{x}{2} + \frac{x^2}{3} - \frac{x^3}{4} - \frac{1}{2}\left(\frac{x^2}{4} - \frac{x^3}{3}\right) - \frac{x^3}{24} + o(x^3) \\
&= -\frac{x}{2} + \frac{x^2}{3} - \frac{x^3}{4} - \frac{x^2}{8} + \frac{x^3}{6} - \frac{x^3}{24} + o(x^3) \\
&= -\frac{x}{2} + \left(\frac{1}{3} - \frac{1}{8}\right)x^2 + \left(-\frac{1}{4} + \frac{1}{6} - \frac{1}{24}\right)x^3 + o(x^3) \\
&= -\frac{x}{2} + \frac{5}{24}x^2 + \left(-\frac{6+4-1}{24}\right)x^3 + o(x^3) \quad(\text{这里仔细算})\\
\end{aligned}
$$

其实我们不必展到三阶，因分母是 $x$，只需要一阶项。重点：$\ln\left(\frac{\ln(1+x)}{x}\right) \sim -\frac{x}{2}$（一阶系数非零）。因此

$$
L = \lim_{x\to0} \frac{-\frac{x}{2} + o(x)}{x} = -\frac{1}{2}
$$

**结果**：原式 $= e^{-1/2} = \frac{1}{\sqrt{e}}$。

**点睛**：

- $1^\infty$ 常规操作：取对数、展开到足够阶数（这里只需一阶）。
- 注意复合函数的展开必须层层递进，确保内外阶数匹配。

---

### 【例 1.13】

$$
\lim_{x \to +\infty} (x+e^x)^{\frac{1}{x}}
$$

**分析**：$x+e^x \to \infty$，指数 $\frac1x \to 0$，属 **$\infty^0$** **型**。

**解**：  
取对数：

$$
L = \lim_{x\to+\infty} \frac{\ln(x+e^x)}{x}
$$

此时为 $\frac{\infty}{\infty}$ 型，洛必达一次：

$$
L = \lim_{x\to+\infty} \frac{\frac{1+e^x}{x+e^x}}{1} = \lim_{x\to+\infty} \frac{1+e^x}{x+e^x}
$$

注意 $x$ 相比 $e^x$ 可忽略：分子 $\sim e^x$，分母 $\sim e^x$，所以 $L = 1$。

**原式** $= e^1 = e$。

**点睛**：

- $\infty^0$ 取对数后直接化 $\frac{\infty}{\infty}$，洛必达抓大头即可。
- 无需复杂展开，识别主导项 $e^x$ 是关键。

---

### 【例 1.14】

$$
\lim_{x \to +\infty} \left( x^{\frac{1}{x}} - 1 \right)^{\frac{1}{\ln x}}
$$

**分析**：$x^{1/x} \to 1$（因为 $\frac{\ln x}{x}\to0$），所以括号内 $x^{1/x}-1\to0$；指数 $\frac{1}{\ln x}\to0$，属 **$0^0$** **型**。  
注意这里底数趋近 $0$，整个是幂指结构。

**解**：  
先看 $x^{1/x} - 1$ 的等价无穷小。  
$x^{1/x} = e^{\frac{\ln x}{x}} = 1 + \frac{\ln x}{x} + o\left(\frac{\ln x}{x}\right)$，因此

$$
x^{1/x} - 1 \sim \frac{\ln x}{x}
$$

令原式 $y = \left( x^{1/x} - 1 \right)^{1/\ln x}$，取对数：

$$
\ln y = \frac{1}{\ln x} \cdot \ln\left( x^{1/x} - 1 \right)
$$

利用 $\ln(x^{1/x}-1) \sim \ln\left(\frac{\ln x}{x}\right) = \ln(\ln x) - \ln x$。

$$
\ln y \sim \frac{\ln(\ln x) - \ln x}{\ln x} = \frac{\ln(\ln x)}{\ln x} - 1 \to 0 - 1 = -1 \quad (x\to+\infty)
$$

所以 $y \to e^{-1} = \frac{1}{e}$。

**更严谨写法**：  
令 $L = \lim_{x\to+\infty} \frac{\ln(x^{1/x}-1)}{\ln x}$。  
因为 $x^{1/x}-1 = \frac{\ln x}{x} + o\left(\frac{\ln x}{x}\right)$，有

$$
\ln(x^{1/x}-1) = \ln\left(\frac{\ln x}{x}\left[1+o(1)\right]\right) = \ln(\ln x) - \ln x + \ln(1+o(1))
$$

从而

$$
L = \lim_{x\to+\infty} \frac{\ln(\ln x) - \ln x + o(1)}{\ln x} = \lim_{x\to+\infty} \left( \frac{\ln(\ln x)}{\ln x} - 1 \right) = -1
$$

原式 $= e^L = 1/e$。

**点睛**：

- 遇到 $0^0$ 同样取对数，但要看清底数的等价无穷小。
- 此题复合函数内部等价替换是合法的，因为底数趋于 0 的正数，对数内部可以等价替换。
- 最终化简为对数比阶：$\frac{\ln(\ln x)}{\ln x}\to0$。

---

### 【例 1.15】

$$
\lim_{x \to \infty} \left[ \frac{x^{1+x}}{(1+x)^x} - \frac{x}{e} \right]
$$

**分析**：先去分析 $\frac{x^{1+x}}{(1+x)^x}$，它是无穷大的形式，可能要提公因子。

**解**：  
先变形：

$$
\frac{x^{1+x}}{(1+x)^x} = x \cdot \frac{x^x}{(1+x)^x} = x \left( \frac{x}{1+x} \right)^x = x \left( 1 + \frac{1}{x} \right)^{-x}
$$

因此原式

$$
= x \left(1+\frac{1}{x}\right)^{-x} - \frac{x}{e} = x \left[ \left(1+\frac{1}{x}\right)^{-x} - \frac{1}{e} \right]
$$

当 $x\to\infty$ 时，$(1+\frac{1}{x})^{-x} \to \frac{1}{e}$，括号内是 $0\cdot\infty$ 形式，我们将其变成 $\frac{0}{0}$ 求解。

令 $t = 1/x$，当 $x\to\infty$ 时 $t\to0$。则

$$
x\left[ \left(1+\frac{1}{x}\right)^{-x} - \frac{1}{e} \right] = \frac{ (1+t)^{-1/t} - e^{-1} }{t}
$$

极限转化为

$$
\lim_{t\to0} \frac{ e^{-\frac{\ln(1+t)}{t}} - e^{-1} }{t}
$$

记 $f(t) = e^{-\frac{\ln(1+t)}{t}}$，$f(0) = e^{-1}$。此极限为 $\frac{0}{0}$，可用洛必达或泰勒。

**泰勒展开**：  
先展开 $-\frac{\ln(1+t)}{t}$：

$$
\ln(1+t) = t - \frac{t^2}{2} + \frac{t^3}{3} - \frac{t^4}{4} + o(t^4)
$$

$$
-\frac{\ln(1+t)}{t} = -1 + \frac{t}{2} - \frac{t^2}{3} + \frac{t^3}{4} + o(t^3)
$$

然后

$$
f(t) = e^{-1 + \frac{t}{2} - \frac{t^2}{3} + \frac{t^3}{4} + o(t^3)} = e^{-1} \cdot e^{\frac{t}{2} - \frac{t^2}{3} + \frac{t^3}{4} + o(t^3)}
$$

展开第二个指数：

$$
e^{\frac{t}{2} - \frac{t^2}{3} + \frac{t^3}{4}} = 1 + \left(\frac{t}{2} - \frac{t^2}{3} + \frac{t^3}{4}\right) + \frac{1}{2}\left(\frac{t}{2} - \frac{t^2}{3}\right)^2 + \frac{1}{6}\left(\frac{t}{2}\right)^3 + o(t^3)
$$

$$
= 1 + \frac{t}{2} - \frac{t^2}{3} + \frac{t^3}{4} + \frac{1}{2}\left(\frac{t^2}{4} - \frac{t^3}{3}\right) + \frac{t^3}{48} + o(t^3)
$$

$$
= 1 + \frac{t}{2} - \frac{t^2}{3} + \frac{t^3}{4} + \frac{t^2}{8} - \frac{t^3}{6} + \frac{t^3}{48} + o(t^3)
$$

合并：

- 一阶：$\frac12$
- 二阶：$-\frac13 + \frac18 = -\frac{5}{24}$
- 三阶：$\frac14 - \frac16 + \frac1{48} = \frac{12-8+1}{48} = \frac{5}{48}$

所以

$$
f(t) = e^{-1}\left[ 1 + \frac{t}{2} - \frac{5}{24}t^2 + \frac{5}{48}t^3 + o(t^3) \right]
$$

因此

$$
f(t) - e^{-1} = e^{-1}\left( \frac{t}{2} - \frac{5}{24}t^2 + \frac{5}{48}t^3 + o(t^3) \right)
$$

代入极限：

$$
\frac{f(t)-e^{-1}}{t} = e^{-1}\left( \frac12 - \frac{5}{24}t + \frac{5}{48}t^2 + o(t^2) \right) \to \frac{e^{-1}}{2} = \frac{1}{2e}
$$

原极限即 $\frac{1}{2e}$。

**点睛**：

- 文档提示“提出一个 x”，正是指将原式写为 $x[(1+1/x)^{-x} - 1/e]$。
- 后续就是一个标准的 $\frac{0}{0}$ 极限，可通过换元 $t=1/x$ 后用泰勒展开。
- 展开时注意 $e^{u}$ 的展开系数，细心运算即可。

---

## 三、总结

- **三步走**：判断类型 → 取对数 → 化 $0\cdot\infty$ 为 $\frac{0}{0}$ 或 $\frac{\infty}{\infty}$ → 求极限 → 取指数。
- 特别留意：  
  ① $1^\infty$ 最终结果常见 $e^k$，$k$ 常可通过等价无穷小或泰勒快速得到；  
  ② $\infty^0$ 和 $0^0$ 对底数进行等价无穷小替换时，要注意是否在函数内部合法（如对数内部可用等价）；  
  ③ 复杂结构先尝试恒等变形（提公因子、倒代换等），再展开。

如果需要针对某一个例题深入探讨不同解法（如例1.15用洛必达怎么求），我可以继续补充。
