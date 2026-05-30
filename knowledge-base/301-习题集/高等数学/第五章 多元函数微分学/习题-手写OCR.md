# 301-高数基础习题-多元微分学


## 第 1 页

多元微分学

2026年5月22日 10:03

1. (1) $\lim_{(x,y)\to(0,0)} \frac{\sqrt{x^2+y^2+1}-1}{x^2+y^2}$

$= \lim_{(x,y)\to(0,0)} \frac{\frac{1}{2}(x^2+y^2)}{(x^2+y^2)} = \frac{1}{2}$

(2) $\lim_{(x,y)\to(0,1)} \frac{\sin(x^2+y^2)}{x^2+y^2}$

连续：$=\frac{\sin 1}{1} = \sin 1$

(3) $\lim_{(x,y)\to(0,0)} \sqrt{x^2+y^2} \sin\left(\frac{1}{\sqrt{x^2+y^2}}\right) = 0$

$\underbrace{0}_{\text{ }} \quad \underbrace{\text{振荡有界量}}$

2. (1) $z_x = \frac{\sqrt{x^2+y^2} - x \cdot \frac{x}{\sqrt{x^2+y^2}}}{x^2+y^2} = \frac{y^2}{(x^2+y^2)^{\frac{3}{2}}}$

$z_y = \frac{0 \cdot \sqrt{x^2+y^2} - y \cdot \frac{1}{\sqrt{x^2+y^2}}}{x^2+y^2} = \frac{-xy}{(x^2+y^2)^{3/2}}$

$z_y = 2x\sqrt{x^2+y^2} \cdot 2y = 4xy\sqrt{x^2+y^2}$.

(2) (-) $a^x$ 视角，$z = \left(\frac{1}{3}\right)^{-\frac{y}{x}}$

$z_x = (1 \div) ^{-\frac{y}{x}} \cdot \ln \frac{1}{1} \cdot \frac{y}{x^2}$

## 第 2 页

$${ z _ { x } = ( \frac { 1 } { 3 } ) ^ { - \frac { y } { x } } \cdot \ln \frac { 1 } { 3 } \cdot \frac { y } { x ^ { 2 } } }$$
$${ z _ { y } = ( \frac { 1 } { 3 } ) ^ { - \frac { y } { x } } \cdot \ln \frac { 1 } { 3 } \cdot ( - \frac { 1 } { x } ) }$$
$$( = ) z = e ^ { - \frac { y } { x } \ln ( \frac { 1 } { 3 } ) }$$
$$z _ { x } = e ^ { - \frac { y } { x } \ln ( \frac { 1 } { 3 } ) } \cdot \frac { y } { x ^ { 2 } } ( \ln \frac { 1 } { 3 } )$$
$$z _ { y } = e ^ { - \frac { y } { x } \ln ( \frac { 1 } { 3 } ) } \cdot - \frac { 1 } { x } ( \ln \frac { 1 } { 3 } )$$

(3) $${ z = \frac { x + y } { x - y } \sin ( \frac { x } { y } ) }$$
$$\begin{aligned} z _ { x } & = \frac { 1 \cdot ( x - y ) - 1 \cdot ( x + y ) } { ( x - y ) ^ { 2 } } \cdot \sin ( \frac { x } { y } ) + \frac { x + y } { x - y } \cos ( \frac { x } { y } ) \cdot \frac { 1 } { y } \\ & = \frac { - 2 y } { ( x - y ) ^ { 2 } } \sin ( \frac { x } { y } ) + \frac { x + y } { x - y } \cos ( \frac { x } { y } ) \cdot \frac { 1 } { y } \end{aligned}$$
$$\begin{aligned} z _ { y } & = \frac { ( x - y ) - ( x + y ) } { ( x - y ) ^ { 2 } } \sin \frac { x } { y } + \frac { x + y } { x - y } \cos ( \frac { x } { y } ) ( - \frac { x } { y ^ { 2 } } ) \\ & = \frac { - 2 y } { ( x - y ) ^ { 2 } } \sin \frac { x } { y } + \frac { x + y } { x - y } \cos \frac { x } { y } ( - \frac { x } { y ^ { 2 } } ) \end{aligned}$$

(4) $$z = \frac { e ^ { x y } } { e ^ { x } + e ^ { y } }$$
$$z _ { x } = \frac { e ^ { x y } \cdot y ( e ^ { x } + e ^ { y } ) - e ^ { x } \cdot e ^ { x y } } { ( e ^ { x } + e ^ { y } ) ^ { 2 } }$$

## 第 3 页

$$z _ { y } = \frac { e ^ { x y } \cdot x ( e ^ { x } + e ^ { y } ) - e ^ { y } \cdot e ^ { x y } } { ( e ^ { x } + e ^ { y } ) ^ { 2 } }$$

(5) $z=\ln\left[\tan\left(\frac{x}{y}\right)\right]$

$z_{x}=\frac{1}{\tan\left(\frac{x}{y}\right)} \sec^{2}\left(\frac{x}{y}\right) \cdot \frac{1}{y}$

$z_{y}=\frac{1}{\tan\left(\frac{x}{y}\right)} \sec^{2}\left(\frac{x}{y}\right)\left(-\frac{x}{y^{2}}\right)$

(6) $z=\arcsin(3-2xy)+\sin\left(3-\frac{2x}{y}\right)$

$z_{x}=\frac{-2y}{\sqrt{1-(3-2xy)^{2}}}+\cos\left(3-\frac{2x}{y}\right)\left(-\frac{2}{y}\right)$

$z_{y}=\frac{-2x}{\sqrt{1-(3-2xy)^{2}}}+\cos\left(3-\frac{2x}{y}\right)\frac{2x}{y^{2}}$

(7) $z=\arctan\sqrt{xy}$

$z_{x}=\frac{\frac{1}{2}yx^{\left(\frac{1}{2}y-1\right)}}{1+x^{y}}$

$z_{y}=\frac{x^{\frac{1}{2}y}\ln x}{1+x^{y}}$

$\left(x^{\frac{1}{2}a}\right)^{\prime}$

$a^{\frac{1}{2}y}$

(8) $z=(1+xy)^{x+y}=e^{(x+y)\ln(1+xy)}$

$z_{x}=e^{(x+y)\ln(1+xy)}\left[y\ln(1+xy)+\frac{y(x+y)}{1+xy}\right]$

## 第 4 页

```latex
\begin{align*}
z_x &= e^{(x+y)\ln(1+xy)} \cdot \left[ y\ln(1+xy) + \frac{y}{1+xy} \right] \\
z_y &= e^{(x+y)\ln(1+xy)} \cdot \left[ x\ln(1+xy) + \frac{x(x+y)}{1+xy} \right]
\end{align*}

3. (1) $f(x,y)=x+y-\sqrt{x^2+y^2}$

$f'_x(3,4)=(x+4-\sqrt{x^2+8})'$

$= 1 - \frac{2x}{2\sqrt{x^2+8}} \bigg|_{x=3} = 1 - \frac{3}{\sqrt{17}}$

(2) $z(x,y)=\ln(x+\frac{y}{2x})$,

$\frac{\partial z}{\partial x}\bigg|_{(1,0)} = (\ln x)' = \frac{1}{x}\bigg|_{x=1} = 1$

(3) $z(x,y)=(1+xy)^y$

$\frac{\partial z}{\partial x}\bigg|_{(1,1)} = (1+x)' = 1$

$\frac{\partial z}{\partial y}\bigg|_{(1,1)} = [(1+y)^y]' = e^{y\ln(1+y)}(\ln(1+y)+\frac{y}{1+y})\bigg|_{y=1}$

$= e^{\ln 2}(\ln 2 + \frac{1}{2}) = 2\ln 2 + 1$

(4) $f(x,y)=x+(y-1)\arcsin\frac{x}{y}$,

$\frac{\partial f}{\partial x}\bigg|_{(1,1)} = (x)' = 1$
```

## 第 5 页

```markdown
4. (1) $z = x^2y^2 - 3xy^3 - xy + 1$

$\frac{\partial z}{\partial x} = 2xy^2 - 3y^3 - y$, $\frac{\partial z}{\partial y} = 2x^2y - 9xy^2 - x$

$\frac{\partial^2 z}{\partial x^2} = 2y^2$; $\frac{\partial^2 z}{\partial y^2} = 2x^2 - 18x$

$\frac{\partial^2 z}{\partial x \partial y} = 4xy - 9y^2 - 1$

(2) $z = y\sin x + xe^y$

$\frac{\partial z}{\partial x} = y\cos x + e^y$, $\frac{\partial z}{\partial y} = \sin x + xe^y$

$\frac{\partial^2 z}{\partial x^2} = -\sin x(y)$, $\frac{\partial^2 z}{\partial y^2} = xe^y$

$\frac{\partial^2 z}{\partial x \partial y} = \cos x + e^y$

(3) $z = \sin^2(2x+3y)$

$z_x = 2\sin(2x+3y)\cos(2x+3y) \cdot 2$

$= 2\sin(4x+6y)$

$z_y = 2\sin(2x+3y)\cos(2x+3y) \cdot 3$

$= 3\sin(4x+6y)$

$z_{xx} = 2\cos(4x+6y) \cdot 4 = 8\cos(4x+6y)$

$z_{xy} = 2\cos(4x+6y) \cdot 6 = 12\cos(4x+6y)$

分区 高数基础习题 的第5页
```

## 第 6 页

$z_{xy} = 2 \cos (4x + 6y) \cdot 6 = 12 \cos (4x + 6y)$

$z_{yy} = 3 \cos (4x + 6y) \cdot 6 = 18 \cos (4x + 6y)$

(4) $z = \arctan \left( \frac{x+y}{1-xy} \right)$

$z_x = \frac{1}{1 + \left( \frac{x+y}{1-xy} \right)^2} \cdot \frac{1 \cdot (1-xy) + y(x+y)}{(1-xy)^2}$

$= \frac{(1-xy)^2}{(x+y)^2 + (1-xy)^2} \cdot \frac{1-y^2}{(1-xy)^2}$ （划掉 $(1-xy)^2$）

$= \frac{1-y^2}{x^2 + y^2 + 2xy + 1 - 2xy + x^2y^2}$ （划掉 $2xy$ 和 $-2xy$）

$= \frac{1-y^2}{x^2 + y^2 + x^2y^2 + 1}$

$z_y = \frac{1}{1 + \left( \frac{x+y}{1-xy} \right)^2} \cdot \frac{1 \cdot (1-xy) + x(x+y)}{(1-xy)^2}$

$= \frac{1-x^2}{x^2 + y^2 + x^2y^2 + 1}$

$z_{xx} = \frac{0(\quad) - (1-y^2)(2x + 2xy^2)}{(1 + x^2 + y^2 + x^2y^2)^2}$

$z_{xy} = \frac{-2y(\quad) - (1-y^2)(2y + 2yx^2)}{(1 + x^2 + y^2 + x^2y^2)^2}$

$z_{yy} = \frac{0(\quad) - (1-x^2)(2y + 2yx^2)}{\quad}$

## 第 7 页

$${ z } _ { y y } = \frac { 0 ( ) - ( 1 - x ^ { 2 } ) ( 2 y + 2 y x ^ { 2 } ) } { ( 1 + x ^ { 2 } + y ^ { 2 } + x ^ { 2 } y ^ { 2 } ) ^ { 2 } }$$

(5) $z = x ^ { y }$

$\begin{array} { l } { { z _ { x } = y x ^ { y - 1 } , \ z _ { y } = x ^ { y } \ln x } } \\ { { \ } } \\ { { z _ { x x } = y ( y - 1 ) x ^ { y - 2 } , \ z _ { x y } = x ^ { y - 1 } + y x ^ { y - 1 } \ln x } } \\ { { \ } } \\ { { z _ { y y } = x ^ { y } ( \ln x ) ^ { 2 } } } \end{array}$

(6) $z = y ^ { \ln x }$

$\begin{array} { l } { { z _ { x } = y ^ { \ln x } \ln y \cdot \frac { 1 } { x } , \ z _ { y } = \ln x y ^ { ( \ln x - 1 ) } } } \\ { { \ } } \\ { { z _ { x x } = ( \ln y ) ^ { 2 } y ^ { \ln x } \cdot \frac { 1 } { x ^ { 2 } } - \frac { 1 } { x ^ { 2 } } y ^ { \ln x } \ln y } } \\ { { \ } } \\ { { z _ { x y } = \frac { 1 } { x } \frac { 1 } { y } \cdot y ^ { \ln x } + \frac { 1 } { x } \ln y \ln x y ^ { ( \ln x - 1 ) } } } \\ { { \ } } \\ { { z _ { y y } = \ln x ( \ln x - 1 ) y ^ { ( \ln x - 2 ) } } } \end{array}$

$5 . \quad z = \ln \sqrt { x ^ { 2 } + y ^ { 2 } }$

$\begin{array} { r l } { { \frac { \partial z } { \partial x } = { \frac { 2 x } { \sqrt { x ^ { 2 } + y ^ { 2 } } } } \, , } } & { { { \frac { \partial z } { \partial y } } = { \frac { 2 y } { \sqrt { x ^ { 2 } + y ^ { 2 } } } } } } \\ { { \frac { \partial ^ { 2 } z } { \partial x ^ { 2 } } + { \frac { \partial ^ { 2 } z } { \partial y ^ { 2 } } } = { \frac { 2 { \sqrt { x ^ { 2 } + y ^ { 2 } } } - { \frac { 2 x \cdot 2 x } { 2 { \sqrt { x ^ { 2 } + y ^ { 2 } } } } } } { x ^ { 2 } + y ^ { 2 } } } + { \frac { 2 { \sqrt { x ^ { 2 } + y ^ { 2 } } } - { \frac { 2 y ^ { 2 } } { \sqrt { x ^ { 2 } + y ^ { 2 } } } } } { x ^ { 2 } + y ^ { 2 } } } } } \\ { { \ } } & { { = { \frac { 2 x ^ { 2 } + 2 y ^ { 2 } - 4 x ^ { 2 } } { 2 { \sqrt { x ^ { 2 } + y ^ { 2 } } } ) } } + { \frac { 2 x ^ { 2 } + 2 y ^ { 2 } - 4 y ^ { 2 } } { 2 { \sqrt { x ^ { 2 } + y ^ { 2 } } } } } = { \frac { 1 } { \sqrt { x ^ { 2 } + y ^ { 2 } } } } } } \end{array}$

## 第 8 页

$$= \frac { \frac { 2 \sqrt { x ^ { 4 } + y ^ { 2 } ) } } { x ^ { 2 } + y ^ { 2 } } + \frac { 1 } { 2 \sqrt { x ^ { 5 } + y z } } } { 2 ( x ^ { 2 } + y ^ { 2 } ) ^ { 3 / 2 } }$$

6. $u = x ^ { 3 } + y ^ { 3 } + z ^ { 3 } - 3 x y z$
$\frac { \partial u } { \partial x } = 3 x ^ { 2 } - 3 y z , \frac { \partial u } { \partial y } = 3 y ^ { 2 } - 3 x z , \frac { \partial u } { \partial z } = 3 z ^ { 2 } - 3 x y$
$\left( \frac { \partial u } { \partial x } \right) ^ { 2 } + \left( \frac { \partial u } { \partial y } \right) ^ { 2 } + \left( \frac { \partial u } { \partial z } \right) ^ { 2 }$
$= 9 x ^ { 4 } + 9 y ^ { 2 } z ^ { 2 } - 1 8 x ^ { 2 } y z + 9 y ^ { 4 } + 9 x ^ { 2 } z ^ { 2 } - 1 8 x y ^ { 2 } z$
$+ 9 z ^ { 4 } + 9 x ^ { 2 } y ^ { 2 } - 1 8 x y z ^ { 2 }$
$\frac { \partial ^ { 2 } u } { \partial x ^ { 2 } } = 6 x , \frac { \partial ^ { 2 } u } { \partial y ^ { 2 } } = 6 y , \frac { \partial ^ { 2 } u } { \partial z ^ { 2 } } = 6 z$
$\therefore + \cdot + \cdot = 6 ( x + y + z )$

7.(1) $u = \sqrt { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } }$
$\frac { \partial u } { \partial x } = \frac { 2 x } { 2 \sqrt { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } } , \frac { \partial u } { \partial y } = \frac { y } { \sqrt { a u } } , \frac { \partial u } { \partial z } = \frac { z } { \sqrt { a u } }$
$\frac { \partial ^ { 2 } u } { \partial x ^ { 2 } } = \frac { \sqrt { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } - \frac { 2 x ^ { 2 } } { \sqrt { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } } } { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } = ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 1 } { 2 } } - x ^ { 2 } ( u ^ { 2 } ) ^ { \frac { 3 } { 2 } }$
$= ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 1 } { 2 } } - x ^ { 2 } ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 3 } { 2 } }$
$u _ { y y } = ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 1 } { 2 } } - y ^ { 2 } ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 3 } { 2 } }$
$+ \cdots - ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 1 } { 2 } } - z ^ { 2 } ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 3 } { 2 } }$

## 第 9 页

$$u _ { z z } = ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 1 } { 2 } } - z ^ { 2 } ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 3 } { 2 } }$$

$$\begin{array} { r l } { u _ { x x } + u _ { y y } + u _ { z z } = { 3 ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - { \frac { 1 } { 2 } } } } - { ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { 1 - { \frac { 3 } { 2 } } } } } & { { } } \\ { = { \frac { 2 } { \sqrt { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } } } } & { { } = { \frac { 2 } { u } } } \end{array}$$

(2) $u = \frac { 1 } { \sqrt { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } }$

$u _ { x } = \frac { \frac { 1 } { 2 } \sqrt { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } } { x ^ { 2 } + y ^ { 2 } + z ^ { 2 } } = x ( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } ) ^ { - \frac { 3 } { 2 } }$

$\begin{array} { r l } { u _ { x x } = \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 3 } { 2 } } } + x \left( - { \frac { 3 } { 2 } } \right) \cdot 2 x \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 5 } { 2 } } } } & { { } } \\ { = \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 3 } { 2 } } } - 3 x ^ { 2 } \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 5 } { 2 } } } } & { { } } \\ { u _ { y y } = \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 3 } { 2 } } } - 3 y ^ { 2 } \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 5 } { 2 } } } } & { { } } \\ { u _ { z z } = \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 3 } { 2 } } } - 3 z ^ { 2 } \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 5 } { 2 } } } } & { { } } \\ { u _ { x x } + u _ { y y } + u _ { z z } = 3 \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { - { \frac { 3 } { 2 } } } - 3 \left( x ^ { 2 } + y ^ { 2 } + z ^ { 2 } \right) ^ { 1 - { \frac { 5 } { 2 } } } } & { { } } \\ { = 0 } & { { } } \end{array}$

(3) $u = \arctan \frac { y } { x } + \arctan \frac { z } { x }$

$u _ { x } = \frac { - \frac { y } { x ^ { 2 } } } { 1 + ( \frac { y } { x } ) ^ { 2 } } + \frac { - \frac { z } { x ^ { 2 } } } { 1 + ( \frac { z } { x } ) ^ { 2 } }$

$= - \frac { y } { x ^ { 2 } } \cdot \frac { x ^ { 2 } } { x ^ { 2 } + y ^ { 2 } } + ( - \frac { z } { x ^ { 2 } } ) ( \frac { x ^ { 2 } } { x ^ { 2 } + z ^ { 2 } } )$

## 第 10 页

$$\begin{array} { r l } { = - { \frac { y } { x ^ { 2 } } } \cdot { \frac { x } { x ^ { 2 } + y ^ { 2 } } } + ( - { \frac { z } { x ^ { 2 } } } ) \left( { \frac { x } { x ^ { 2 } + z ^ { 2 } } } \right) } & { { } } \\ { = - { \frac { y } { x ^ { 2 } + y ^ { 2 } } } - { \frac { z } { x ^ { 2 } + z ^ { 2 } } } } & { { } } \\ { u _ { y } = { \frac { \frac { 1 } { x } } { 1 + \left( { \frac { y } { x } } \right) ^ { 2 } } } = { \frac { 1 } { x } } \cdot { \frac { x ^ { 2 } } { x ^ { 2 } + y ^ { 2 } } } = { \frac { x } { x ^ { 2 } + y ^ { 2 } } } } & { { } } \\ { u _ { z } = { \frac { \frac { 1 } { x } } { 1 + \left( { \frac { z } { x } } \right) ^ { 2 } } } = { \frac { 1 } { x } } \cdot { \frac { x ^ { 2 } } { x ^ { 2 } + z ^ { 2 } } } = { \frac { x } { x ^ { 2 } + z ^ { 2 } } } } & { { } } \\ { u _ { x x } = - { \frac { 0 - 2 x y } { ( x ^ { 2 } + y ^ { 2 } ) ^ { 2 } } } - { \frac { 0 - 2 x z } { ( x ^ { 2 } + z ^ { 2 } ) ^ { 2 } } } } & { { } } \\ { = { \frac { 2 x y + 2 x z } { ( x ^ { 2 } + y ^ { 2 } ) ^ { 2 } } } } & { { } } \\ { u _ { y y } = { \frac { 0 - 2 x y } { ( x ^ { 2 } + y ^ { 2 } ) ^ { 2 } } } } & { { } u _ { z z } = { \frac { - 2 x z } { ( x ^ { 2 } + y ^ { 2 } ) ^ { 2 } } } } \\ { u _ { x x } + u _ { y y } + u _ { z z } = 0 } & { { } } \end{array}$$

(4) $z = f _ { n } ( e ^ { x } + e ^ { y } )$ ,

$z _ { x } = \frac { e ^ { x } } { e ^ { x } + e ^ { y } } , z _ { y } = \frac { e ^ { y } } { e ^ { x } + e ^ { y } }$

$z _ { x x } = \frac { e ^ { x } \left( e ^ { x } + e ^ { y } \right) + e ^ { 2 x } } { \left( e ^ { x } + e ^ { y } \right) ^ { 2 } } = \frac { 2 e ^ { 2 x } + e ^ { x } e ^ { y } } { \left( e ^ { x } + e ^ { y } \right) ^ { 2 } }$

$z _ { y y } = \frac { e ^ { y } \left( e ^ { x } + e ^ { y } \right) + e ^ { 2 y } } { \left( e ^ { x } + e ^ { y } \right) ^ { 2 } } = \frac { 2 e ^ { 2 y } + e ^ { x } e ^ { y } } { \left( e ^ { x } + e ^ { y } \right) ^ { 2 } }$

$z _ { x y } = \frac { 0 - e ^ { x } e ^ { y } } { \dots }$

## 第 11 页

$$z _ { x y } = \frac { 0 - e ^ { x } e ^ { y } } { ( e ^ { x } + e ^ { y } ) ^ { 2 } } \qquad z _ { x x } + z _ { x y } + z _ { y y } = 0 .$$

8.(1) $z=f_{n}\left(x^{2}+y^{2}\right)$

(一) $z_{x}=\frac{2 x}{x^{2}+y^{2}}, z_{y}=\frac{2 y}{x^{2}+y^{2}}$

$\mathrm{d} z=\frac{2 x}{x^{2}+y^{2}} \mathrm{~d} x+\frac{2 y}{x^{2}+y^{2}} \mathrm{~d} y$

$(二) \mathrm{d} z=\frac{2 x \mathrm{~d} x+2 y \mathrm{~d} y}{x^{2}+y^{2}}$

(2) $\begin{aligned} \mathrm{d} z & =\frac{\sqrt{x^{2}+y^{2}} \mathrm{~d} x-x \frac{x \mathrm{~d} x}{2 \sqrt{x^{2}+y^{2}}}}{\left(x^{2}+y^{2}\right)}+\frac{\sqrt{x^{2}+y^{2}} \mathrm{~d} y-x \frac{y \mathrm{~d} y}{2 \sqrt{x^{2}+y^{2}}}}{x^{2}+y^{2}} \\ & =\left(\frac{1}{\sqrt{x^{2}+y^{2}}}-\frac{x^{2}}{\left(x^{2}+y^{2}\right)^{3 / 2}}\right) \mathrm{d} x+\left(\frac{1}{\sqrt{x^{2}+y^{2}}}-\frac{2 x y}{\left(x^{2}+y^{2}\right)^{3 / 2}}\right) \mathrm{d} y \end{aligned}$

(3) $\mathrm{d} z=$