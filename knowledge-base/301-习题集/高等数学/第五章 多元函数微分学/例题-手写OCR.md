# 301-高数基础例题-多元微分学


## 第 1 页

多元微分学

2026年5月21日 11:10

一、基本概念

极限存在性.

1. $\lim_{(x,y)\to(0,0)} \frac{xy}{x^2+y^2}$

令 $y=kx$, $\lim_{(x,y)\to(0,0)} \frac{kx^2}{(1+k^2)x^2} = \frac{k}{1+k^2}$

极限随 $k$ 变化

2. $\lim_{(x,y)\to(0,0)} \frac{xy^2}{x^2+y^2}$

$0 \le \lim_{(x,y)\to(0,0)} \left| \frac{xy^2}{x^2+y^2} \right| \le \left| \frac{xy^2}{2xy} \right| = 0$

$\lim_{x\to0} \frac{|y|}{2} = 0$

$x^2+y^2-2xy \ge 0$ 极限为0

$x^2+y^2 \ge 2xy$

函数连续性

1. $f(x,y) = \frac{\sin(x^2+y)}{xy}$

$\lim_{(x,y)\to(0,0)} \frac{\sin(x^2+y)}{xy} = 1 \frac{x^2+y}{xy}$

## 第 2 页

$(x,y)\to(0,0)$ $\quad xy$ $\quad xy$

令 $y=kx$, $\lim \frac{kx+x^2}{kx^2} = \frac{1}{k}$

定义域：$xy\neq 0$，整个平面去掉两条坐标轴区域上
有定义且连续.

在 $xy=0$ 处无定义不连续

$z$ , $f(x,y) = \begin{cases} \frac{x^2y}{x^2+y^2}, & (x,y)\neq(0,0) \\ 0, & (x,y)=(0,0) \end{cases}$

$\lim_{(x,y)\to(0,0)} \frac{x^2y}{x^2+y^2} = 0$ 见上，连续.

二、偏导

1. $u=x^y$ 偏导 $u_x, u_y$.

$u_x = y x^{y-1}$ $(x^a)'$

$u_y = x^y \ln x$ $(a^x)' = a^x \ln a$

2. $z=\frac{x}{\sqrt{x^2+y^2}}$, $z_x(0,1), z_y(0,1)$

$z_x = \left. \frac{\sqrt{x^2+y^2} - \frac{2x^2}{2\sqrt{x^2+y^2}}}{x^2+y^2} \right|_{\substack{x=0 \\ y=1}} = \frac{1-0}{1} = 1$ ✓

## 第 3 页

$x^{2}+y^{2}$

$\begin{cases} x=0 \\ y=1 \end{cases}$

or 先代后求，反正 $y=1$ 恒定。

$z_{x}(0,1)=\left(\frac{x}{\sqrt{x^{2}+1}}\right)^{\prime}=\frac{\sqrt{x^{2}+1}-\frac{2 x^{2}}{\sqrt{x^{2}+1}}}{x^{2}+1}=1$

$z_{y}(0,1)=(0)^{\prime}=0$

高阶偏导.

$f(x, y)=\ln x+\sin \left(x e^{y}\right)$

$f_{x}=\frac{1}{x}+\cos \left(x e^{y}\right) \cdot e^{y}$

$f_{x x}=-\frac{1}{x^{2}}+\left(-\sin \left(x e^{y}\right) \cdot\left(e^{y}\right)^{2}\right)$

$=-\frac{1}{x^{2}}-e^{2 y} \sin \left(x e^{y}\right)$

$f_{x y}=-\sin \left(x e^{y}\right) \cdot x e^{2 y}+\cos \left(x e^{y}\right) \cdot e^{y}$

$f_{y}=\cos \left(x e^{y}\right) x e^{y}$

$f_{y x}=-\sin \left(x e^{y}\right) \cdot x e^{2 y}+\cos \left(x e^{y}\right) e^{y}$

$f_{y y}=-\sin \left(x e^{y}\right) x^{2} e^{2 y}+\cos \left(x e^{y}\right) x e^{y}$

全微分: $\Delta z=A \Delta x+B \Delta y+O\left(\sqrt{(\Delta x)^{2}+(\Delta y)^{2}}\right)$

一元可微, $\Delta y=A \Delta x+o(\Delta x)$

$d z=A d x+B d y$

## 第 4 页

- 元可微，$\Delta y = A \Delta x + o(\Delta x)$

$$
\lim_{\Delta x \to 0} \Delta y = \lim_{\Delta x \to 0} A \Delta x + 0
$$

$$
\lim_{\Delta x \to 0} \frac{\Delta y}{\Delta x} = \lim_{\Delta x \to 0} \frac{f(x_0 + \Delta x) - f(x_0)}{\Delta x} = f'(x_0) = A
$$

可微必连续：$\Rightarrow \lim_{\substack{\Delta x \to 0 \\ \Delta y \to 0}} f(x_0 + \Delta x, y_0 + \Delta y) = f(x_0, y_0)$

证：

$$
\underbrace{f(x_0 + \Delta x, y_0 + \Delta y) - f(x_0, y_0)}_{\substack{\lim \\ \Delta x \to 0 \\ \Delta y \to 0}} = A \Delta x + B \Delta y + o(\rho)
$$

即

可微必可偏导（偏导存在）

$$
\int_{\Delta x \to 0} \frac{f(x_0 + \Delta x, y_0) - f(x_0, y_0)}{\Delta x} = \text{constant}
$$

$$
\lim_{\substack{\Delta x \to 0 \\ \Delta y \to 0}} [f(x_0 + \Delta x, y_0 + \Delta y) - f(x_0, y_0)] = \lim_{\substack{\Delta x \to 0 \\ \Delta y \to 0}} [A \Delta x + B \Delta y + o(\rho)]
$$

令 $\Delta x \to 0, \Delta y = 0$，

$$
\lim_{\Delta x \to 0} [f(x_0 + \Delta x, y_0) - f(x_0, y_0)] = \lim_{\Delta x \to 0} [A \Delta x + o(\Delta x)]
$$

$$
\Rightarrow \lim_{\Delta x \to 0} \frac{f(x + \Delta x, y_0) - f(x_0, y_0)}{\Delta x} = A = f_x(x_0, y_0)
$$

## 第 5 页

```markdown
1. $z=\arctan\frac{y}{x}$ 全微分

(一)
$z_x = \frac{-\frac{y}{x^2}}{1+(\frac{y}{x})^2} = -\frac{y}{x^2} \cdot \frac{x^2}{x^2+y^2} = \frac{-y}{x^2+y^2}$

$z_y = \frac{\frac{1}{x}}{1+(\frac{y}{x})^2} = \frac{1}{x} \cdot \frac{x^2}{x^2+y^2} = \frac{x}{x^2+y^2}$

$dz = \frac{-y}{x^2+y^2} dx + \frac{x}{x^2+y^2} dy$

(二) $d(\frac{y}{x}) = \frac{xdy-ydx}{x^2}$, $dy=y'dx$ (红色标注)

$$
\begin{aligned}
dz &= d(\arctan\frac{y}{x}) \\
&= \frac{1}{1+(\frac{y}{x})^2} d(\frac{y}{x}) \\
&= \frac{x^2}{x^2+y^2} \cdot \frac{xdy-ydx}{x^2} = \frac{xdy-ydx}{x^2+y^2}
\end{aligned}
$$

可微判定方法:

可微
$\Delta z = f_x \Delta x + f_y \Delta y + o(\sqrt{(\Delta x)^2+(\Delta y)^2})$

$\iff \lim_{\substack{\Delta x \to 0 \\ \Delta y \to 0}} \frac{\Delta z - f_x \Delta x - f_y \Delta y}{\sqrt{(\Delta x)^2+(\Delta y)^2}} = 0$

分区 高数基础例题 的第5页
```

## 第 6 页

$f(x, y)=\left\{\begin{array}{c} \frac{\sin (x y)}{\sqrt{x^{2}+y^{2}}},(x, y) \neq(0,0) \\ 0,(x, y)=(0,0) \end{array}\right.$ 在 $(0,0)$ 处

$\lim _{\substack{x \rightarrow 0 \\ y \rightarrow 0}} \frac{\sin (x y)}{\sqrt{x^{2}+y^{2}}}=\lim _{\substack{x \rightarrow 0 \\ y \rightarrow 0}} \frac{x y}{\sqrt{x^{2}+y^{2}}}=\lim _{\substack{x \rightarrow 0 \\ y \rightarrow 0}}\left|\frac{x y}{\sqrt{x^{2}+y^{2}}}\right| \Delta$

$0 \leq \Delta \leq \lim _{\substack{x \rightarrow 0 \\ y \rightarrow 0}} \frac{|x y|}{|x|}=|y|=0=f(0,0)$

极限存在 $\downarrow$ 连续.

$f_{x}(0,0)=\lim _{\substack{\Delta x \rightarrow 0 \\ y=0}} \frac{f(0+\Delta x, 0)-f(0,0)}{\Delta x}=0$

同理 $f_{y}(0,0)=0$, 偏导存在

$\lim _{\substack{\Delta x \rightarrow 0 \\ \Delta y \rightarrow 0}} \frac{\Delta z-f_{x} \Delta x-f_{y} \Delta y}{\sqrt{(\Delta x)^{2}+(\Delta y)^{2}}}=\lim _{\substack{\Delta x \rightarrow 0 \\ \Delta y \rightarrow 0}} \frac{f(0+\Delta x, 0+\Delta y)-f(0,0)-0-0}{\sqrt{(\Delta x)^{2}+(\Delta y)^{2}}}$

$=\lim _{\substack{\Delta x \rightarrow 0 \\ \Delta y \rightarrow 0}} \frac{\sin (\Delta x \Delta y)}{\sqrt{(\Delta x)^{2}+(\Delta y)^{2}}} \cdot \frac{1}{\sqrt{(\Delta x)^{2}+(\Delta y)^{2}}}$

$=\lim _{\substack{\Delta x \rightarrow 0 \\ \Delta y \rightarrow 0}} \frac{\Delta x \Delta y}{(\Delta x)^{2}+(\Delta y)^{2}} \xrightarrow{\text { 令 } \Delta y=k \Delta x} \lim _{\substack{\Delta x \rightarrow 0 \\ \Delta y \rightarrow 0}} \frac{k(\Delta x)^{2}}{1+k^{2}(\Delta x)^{2}}=\frac{k}{1+k^{2}}$

极限不存，不可微

多元复合函数微分法

## 第 7 页

多元复合函数求偏导数

1. $z = e^u \sin v$，$u = \frac{x^2}{y}$，$v = x^2 - xy + y^2$，求 $z_x, z_y$

(一)
$$
z_x = e^u \sin v \cdot \frac{2x}{y} + e^u \cos v (2x - y)
$$
$$
z_y = e^u \sin v \left(-\frac{2x}{y^2}\right) + e^u \cos v (-x + 2y)
$$

(二)
$$
z_x = z_1 \cdot \frac{2x}{y} + z_2 (2x - y).
$$

2. $z = f(u, v, x, y)$，$u = u(x, y)$，$v = v(x, y)$

(一)
$$
z_x = z_u u_x + z_v v_x + f_x = f_u u_x + f_v v_x + f_x
$$
$$
z_y = z_u u_y + z_v v_y + f_y
$$

(二)
$$
z_x = f_1 u_1 + f_2 v_1 + f_3 + 0 \cdot f_4
$$
$$
z_y = f_1 u_2 + f_2 v_2 + f_4
$$

3. $z = f\left(x - y, \frac{x}{y}\right)$，求 $z_x, z_y$

$$
z_x = f_1' \cdot 1 + f_2' \cdot \frac{1}{y}
$$
$$
z_y = f_1' \cdot (-1) + f_2' \cdot \left(-\frac{x}{y^2}\right).
$$

## 第 8 页

4. $z = f(x^2 - y^2, \varphi(xy))$

$\frac{\partial[\varphi(xy)]}{\partial x} = \frac{d[\varphi(xy)]}{d(xy)} \cdot \frac{\partial(xy)}{\partial x}$

(1) $x z_x - y z_y$

$z_x = f_1 2x + f_2 \varphi'_x \cdot y$

$z_y = f_1 (-2y) + f_2 \varphi'_y \cdot x$

$x z_x - y z_y = 2(x^2 + y^2)f_1$

(2) $z_{xx} = 2f_1 + 2x(f_{11}2x + f_{12}\varphi'y) + $

$\varphi''f_2y^2 + \varphi'y(f_{21}2x + f_{22}\varphi'y)$

(九) 隐函数的偏导数

1. $z = z(x, y): x + y + z = e^{2z}$，求 $z_{xy}$

$\frac{1 + z_x}{1} = e^{2z} \cdot 2z_x$

$\downarrow$

$1 = (2e^{2z} - 1)z_x \Rightarrow z_x = \frac{1}{2e^{2z} - 1}$

$\downarrow$

$z_{xy} =$

$z_{xy} = e^{2z} 2z_y \cdot 2z_x + e^{2z} \cdot 2z_{xy}$

$(1 - 2e^{2z})z_{xy} = 4z_x z_y e^{2z}$

$z_{xy} = \frac{4e^{2z}z_x z_y}{1 - 2e^{2z}}$

## 第 9 页

$z_{x}、z_{y}$ 都可算出代入.

2. $u=u(x, y): u=\varphi(u)+\int_{y}^{x} p(t) d t, \varphi^{\prime}(u) \neq 1$

$z=f(u)$, 求 $p(y) z_{x}+p(x) z_{y}$

$\begin{aligned} & u_{x}=\underbrace{\varphi^{\prime}(u)}_{\text { }} \cdot u_{x}+p(x) \rightarrow\left[1-\varphi^{\prime}(u)\right] u_{x}=p(x) \\ & z_{x}=f^{\prime} u_{x} \leftarrow \overparen{u_{x}=\frac{p(x)}{1-\varphi^{\prime}(u)}} \\ & =f^{\prime}\left[\underbrace{\varphi_{x} u_{x}+p(x)}_{u \text { 是隐函数 }}\right] \end{aligned}$

$\begin{aligned} & u_{y}=\varphi^{\prime}(u) u_{y}-p(y) \rightarrow u_{y}=\frac{-p(y)}{1-\varphi^{\prime}(u)} \\ & z_{y}=\underbrace{f^{\prime}(u)\left[\varphi^{\prime}(u) u_{y}-p(y)\right]}_{\substack{= \\ 1-\varphi^{\prime}(u)}} \frac{f^{\prime}(u) p(y)}{1-\varphi^{\prime}(u)} \\ & p(y) z_{x}+p(x) z_{y}= \end{aligned}$