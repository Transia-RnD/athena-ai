`
`
`
m
a
r
k
d
o
w
n


#
 
X
R
P
L
 
C
r
y
p
t
o
g
r
a
p
h
y
 
F
u
n
c
t
i
o
n
a
l
i
t
y
:
 
C
o
m
p
r
e
h
e
n
s
i
v
e
 
D
o
c
u
m
e
n
t
a
t
i
o
n




T
h
i
s
 
d
o
c
u
m
e
n
t
 
p
r
o
v
i
d
e
s
 
a
 
d
e
t
a
i
l
e
d
,
 
c
o
d
e
-
l
e
v
e
l
 
b
r
e
a
k
d
o
w
n
 
o
f
 
t
h
e
 
c
r
y
p
t
o
g
r
a
p
h
y
 
f
u
n
c
t
i
o
n
a
l
i
t
y
 
i
n
 
t
h
e
 
X
R
P
L
 
(
X
R
P
 
L
e
d
g
e
r
)
 
s
o
u
r
c
e
 
c
o
d
e
.
 
I
t
 
c
o
v
e
r
s
 
a
l
l
 
m
a
j
o
r
 
c
r
y
p
t
o
g
r
a
p
h
i
c
 
c
o
m
p
o
n
e
n
t
s
,
 
t
h
e
i
r
 
i
m
p
l
e
m
e
n
t
a
t
i
o
n
,
 
e
r
r
o
r
 
h
a
n
d
l
i
n
g
,
 
s
u
p
p
o
r
t
e
d
 
a
l
g
o
r
i
t
h
m
s
,
 
k
e
y
 
f
o
r
m
a
t
s
,
 
t
h
r
e
a
d
 
s
a
f
e
t
y
,
 
e
x
t
e
n
s
i
b
i
l
i
t
y
,
 
p
a
r
a
m
e
t
e
r
/
r
e
t
u
r
n
 
t
y
p
e
s
,
 
u
s
a
g
e
 
e
x
a
m
p
l
e
s
,
 
a
n
d
 
s
e
c
u
r
i
t
y
 
b
e
s
t
 
p
r
a
c
t
i
c
e
s
,
 
s
t
r
i
c
t
l
y
 
g
r
o
u
n
d
e
d
 
i
n
 
t
h
e
 
p
r
o
v
i
d
e
d
 
s
o
u
r
c
e
 
c
o
d
e
 
a
n
d
 
e
x
p
l
a
n
a
t
i
o
n
s
.




-
-
-




#
#
 
T
a
b
l
e
 
o
f
 
C
o
n
t
e
n
t
s




-
 
[
K
e
y
 
M
a
n
a
g
e
m
e
n
t
]
(
#
k
e
y
-
m
a
n
a
g
e
m
e
n
t
)


-
 
[
R
a
n
d
o
m
 
N
u
m
b
e
r
 
G
e
n
e
r
a
t
i
o
n
]
(
#
r
a
n
d
o
m
-
n
u
m
b
e
r
-
g
e
n
e
r
a
t
i
o
n
)


-
 
[
H
a
s
h
 
F
u
n
c
t
i
o
n
s
]
(
#
h
a
s
h
-
f
u
n
c
t
i
o
n
s
)


-
 
[
D
i
g
i
t
a
l
 
S
i
g
n
a
t
u
r
e
s
]
(
#
d
i
g
i
t
a
l
-
s
i
g
n
a
t
u
r
e
s
)


-
 
[
S
e
c
u
r
e
 
M
e
m
o
r
y
 
E
r
a
s
u
r
e
]
(
#
s
e
c
u
r
e
-
m
e
m
o
r
y
-
e
r
a
s
u
r
e
)


-
 
[
S
S
L
/
T
L
S
 
C
o
n
t
e
x
t
 
a
n
d
 
H
a
n
d
s
h
a
k
e
 
S
e
c
u
r
i
t
y
]
(
#
s
s
l
t
l
s
-
c
o
n
t
e
x
t
-
a
n
d
-
h
a
n
d
s
h
a
k
e
-
s
e
c
u
r
i
t
y
)


-
 
[
C
o
m
p
o
n
e
n
t
 
I
n
t
e
r
a
c
t
i
o
n
s
]
(
#
c
o
m
p
o
n
e
n
t
-
i
n
t
e
r
a
c
t
i
o
n
s
)


-
 
[
E
r
r
o
r
 
H
a
n
d
l
i
n
g
]
(
#
e
r
r
o
r
-
h
a
n
d
l
i
n
g
)


-
 
[
S
u
p
p
o
r
t
e
d
 
K
e
y
 
T
y
p
e
s
 
a
n
d
 
A
l
g
o
r
i
t
h
m
s
]
(
#
s
u
p
p
o
r
t
e
d
-
k
e
y
-
t
y
p
e
s
-
a
n
d
-
a
l
g
o
r
i
t
h
m
s
)


-
 
[
K
e
y
 
F
o
r
m
a
t
 
D
e
t
a
i
l
s
]
(
#
k
e
y
-
f
o
r
m
a
t
-
d
e
t
a
i
l
s
)


-
 
[
T
h
r
e
a
d
 
S
a
f
e
t
y
]
(
#
t
h
r
e
a
d
-
s
a
f
e
t
y
)


-
 
[
E
x
t
e
n
s
i
b
i
l
i
t
y
]
(
#
e
x
t
e
n
s
i
b
i
l
i
t
y
)


-
 
[
P
a
r
a
m
e
t
e
r
 
a
n
d
 
R
e
t
u
r
n
 
T
y
p
e
s
]
(
#
p
a
r
a
m
e
t
e
r
-
a
n
d
-
r
e
t
u
r
n
-
t
y
p
e
s
)


-
 
[
U
s
a
g
e
 
E
x
a
m
p
l
e
s
]
(
#
u
s
a
g
e
-
e
x
a
m
p
l
e
s
)


-
 
[
S
e
c
u
r
i
t
y
 
W
a
r
n
i
n
g
s
 
a
n
d
 
B
e
s
t
 
P
r
a
c
t
i
c
e
s
]
(
#
s
e
c
u
r
i
t
y
-
w
a
r
n
i
n
g
s
-
a
n
d
-
b
e
s
t
-
p
r
a
c
t
i
c
e
s
)


-
 
[
S
o
u
r
c
e
 
C
o
d
e
 
R
e
f
e
r
e
n
c
e
s
]
(
#
s
o
u
r
c
e
-
c
o
d
e
-
r
e
f
e
r
e
n
c
e
s
)




-
-
-




#
#
 
K
e
y
 
M
a
n
a
g
e
m
e
n
t




#
#
#
 
S
e
c
r
e
t
K
e
y
 
C
l
a
s
s




-
 
*
*
D
e
f
i
n
i
t
i
o
n
:
*
*
 
 


 
 
T
h
e
 
`
S
e
c
r
e
t
K
e
y
`
 
c
l
a
s
s
 
s
e
c
u
r
e
l
y
 
h
o
l
d
s
 
a
 
3
2
-
b
y
t
e
 
p
r
i
v
a
t
e
 
k
e
y
.


-
 
*
*
C
o
n
s
t
r
u
c
t
i
o
n
:
*
*
 
 


 
 
-
 
C
o
n
s
t
r
u
c
t
e
d
 
f
r
o
m
 
a
 
3
2
-
b
y
t
e
 
a
r
r
a
y
 
o
r
 
a
 
`
S
l
i
c
e
`
.


 
 
-
 
T
h
r
o
w
s
 
i
f
 
t
h
e
 
i
n
p
u
t
 
s
i
z
e
 
i
s
 
n
o
t
 
e
x
a
c
t
l
y
 
3
2
 
b
y
t
e
s
.


-
 
*
*
D
e
s
t
r
u
c
t
i
o
n
:
*
*
 
 


 
 
-
 
T
h
e
 
d
e
s
t
r
u
c
t
o
r
 
s
e
c
u
r
e
l
y
 
e
r
a
s
e
s
 
t
h
e
 
i
n
t
e
r
n
a
l
 
b
u
f
f
e
r
 
u
s
i
n
g
 
`
s
e
c
u
r
e
_
e
r
a
s
e
`
,
 
w
h
i
c
h
 
c
a
l
l
s
 
`
O
P
E
N
S
S
L
_
c
l
e
a
n
s
e
`
.


-
 
*
*
A
c
c
e
s
s
o
r
s
:
*
*
 
 


 
 
-
 
`
d
a
t
a
(
)
`
:
 
R
e
t
u
r
n
s
 
a
 
p
o
i
n
t
e
r
 
t
o
 
t
h
e
 
k
e
y
 
b
y
t
e
s
.


 
 
-
 
`
s
i
z
e
(
)
`
:
 
R
e
t
u
r
n
s
 
3
2
.


 
 
-
 
I
t
e
r
a
t
o
r
s
 
f
o
r
 
b
e
g
i
n
/
e
n
d
.




#
#
#
 
P
u
b
l
i
c
K
e
y
 
C
l
a
s
s




-
 
*
*
D
e
f
i
n
i
t
i
o
n
:
*
*
 
 


 
 
T
h
e
 
`
P
u
b
l
i
c
K
e
y
`
 
c
l
a
s
s
 
h
o
l
d
s
 
a
 
3
3
-
b
y
t
e
 
c
o
m
p
r
e
s
s
e
d
 
p
u
b
l
i
c
 
k
e
y
.


-
 
*
*
C
o
n
s
t
r
u
c
t
i
o
n
:
*
*
 
 


 
 
-
 
C
o
n
s
t
r
u
c
t
e
d
 
f
r
o
m
 
a
 
`
S
l
i
c
e
`
 
o
f
 
3
3
 
b
y
t
e
s
.


-
 
*
*
A
c
c
e
s
s
o
r
s
:
*
*
 
 


 
 
-
 
`
d
a
t
a
(
)
`
,
 
`
s
i
z
e
(
)
`
,
 
a
n
d
 
i
t
e
r
a
t
o
r
s
.


 
 
-
 
`
s
l
i
c
e
(
)
`
:
 
R
e
t
u
r
n
s
 
a
 
`
S
l
i
c
e
`
 
v
i
e
w
.




#
#
#
 
S
e
e
d
 
a
n
d
 
K
e
y
 
G
e
n
e
r
a
t
i
o
n




-
 
*
*
r
a
n
d
o
m
S
e
c
r
e
t
K
e
y
(
)
:
*
*
 
 


 
 
-
 
A
l
l
o
c
a
t
e
s
 
a
 
3
2
-
b
y
t
e
 
b
u
f
f
e
r
.


 
 
-
 
F
i
l
l
s
 
i
t
 
w
i
t
h
 
c
r
y
p
t
o
g
r
a
p
h
i
c
a
l
l
y
 
s
e
c
u
r
e
 
r
a
n
d
o
m
 
b
y
t
e
s
 
u
s
i
n
g
 
`
b
e
a
s
t
:
:
r
n
g
f
i
l
l
`
 
a
n
d
 
`
c
r
y
p
t
o
_
p
r
n
g
(
)
`
.


 
 
-
 
C
o
n
s
t
r
u
c
t
s
 
a
 
`
S
e
c
r
e
t
K
e
y
`
 
f
r
o
m
 
t
h
e
 
b
u
f
f
e
r
.


 
 
-
 
S
e
c
u
r
e
l
y
 
e
r
a
s
e
s
 
t
h
e
 
b
u
f
f
e
r
 
a
f
t
e
r
 
u
s
e
.


 
 
-
 
R
e
t
u
r
n
s
 
t
h
e
 
`
S
e
c
r
e
t
K
e
y
`
.




-
 
*
*
g
e
n
e
r
a
t
e
S
e
c
r
e
t
K
e
y
(
K
e
y
T
y
p
e
 
t
y
p
e
,
 
S
e
e
d
 
c
o
n
s
t
&
 
s
e
e
d
)
:
*
*
 
 


 
 
-
 
F
o
r
 
`
e
d
2
5
5
1
9
`
:
 
H
a
s
h
e
s
 
t
h
e
 
s
e
e
d
 
w
i
t
h
 
`
s
h
a
5
1
2
H
a
l
f
_
s
`
,
 
u
s
e
s
 
t
h
e
 
r
e
s
u
l
t
 
a
s
 
t
h
e
 
s
e
c
r
e
t
 
k
e
y
.


 
 
-
 
F
o
r
 
`
s
e
c
p
2
5
6
k
1
`
:
 
C
a
l
l
s
 
`
d
e
r
i
v
e
D
e
t
e
r
m
i
n
i
s
t
i
c
R
o
o
t
K
e
y
(
s
e
e
d
)
`
 
t
o
 
d
e
t
e
r
m
i
n
i
s
t
i
c
a
l
l
y
 
d
e
r
i
v
e
 
a
 
v
a
l
i
d
 
s
e
c
p
2
5
6
k
1
 
s
e
c
r
e
t
 
k
e
y
.


 
 
-
 
S
e
c
u
r
e
l
y
 
e
r
a
s
e
s
 
t
e
m
p
o
r
a
r
y
 
b
u
f
f
e
r
s
.


 
 
-
 
T
h
r
o
w
s
 
o
n
 
u
n
k
n
o
w
n
 
k
e
y
 
t
y
p
e
.




-
 
*
*
d
e
r
i
v
e
D
e
t
e
r
m
i
n
i
s
t
i
c
R
o
o
t
K
e
y
(
S
e
e
d
 
c
o
n
s
t
&
 
s
e
e
d
)
:
*
*
 
 


 
 
-
 
C
o
p
i
e
s
 
t
h
e
 
s
e
e
d
 
i
n
t
o
 
a
 
2
0
-
b
y
t
e
 
b
u
f
f
e
r
.


 
 
-
 
F
o
r
 
u
p
 
t
o
 
1
2
8
 
a
t
t
e
m
p
t
s
,
 
w
r
i
t
e
s
 
a
 
s
e
q
u
e
n
c
e
 
n
u
m
b
e
r
,
 
h
a
s
h
e
s
 
w
i
t
h
 
`
s
h
a
5
1
2
H
a
l
f
`
,
 
a
n
d
 
c
h
e
c
k
s
 
i
f
 
t
h
e
 
r
e
s
u
l
t
 
i
s
 
a
 
v
a
l
i
d
 
s
e
c
p
2
5
6
k
1
 
k
e
y
.


 
 
-
 
R
e
t
u
r
n
s
 
t
h
e
 
f
i
r
s
t
 
v
a
l
i
d
 
k
e
y
 
f
o
u
n
d
,
 
s
e
c
u
r
e
l
y
 
e
r
a
s
i
n
g
 
t
h
e
 
b
u
f
f
e
r
.


 
 
-
 
T
h
r
o
w
s
 
i
f
 
n
o
 
v
a
l
i
d
 
k
e
y
 
i
s
 
f
o
u
n
d
.




#
#
#
 
K
e
y
 
P
a
i
r
 
G
e
n
e
r
a
t
i
o
n




-
 
*
*
g
e
n
e
r
a
t
e
K
e
y
P
a
i
r
(
K
e
y
T
y
p
e
 
t
y
p
e
,
 
S
e
e
d
 
c
o
n
s
t
&
 
s
e
e
d
)
:
*
*
 
 


 
 
-
 
F
o
r
 
`
s
e
c
p
2
5
6
k
1
`
:
 
U
s
e
s
 
a
 
d
e
t
e
r
m
i
n
i
s
t
i
c
 
d
e
r
i
v
a
t
i
o
n
 
f
r
o
m
 
t
h
e
 
s
e
e
d
,
 
a
p
p
l
i
e
s
 
a
 
t
w
e
a
k
 
(
o
r
d
i
n
a
l
 
0
)
,
 
a
n
d
 
r
e
t
u
r
n
s
 
t
h
e
 
r
e
s
u
l
t
i
n
g
 
k
e
y
p
a
i
r
.


 
 
-
 
F
o
r
 
`
e
d
2
5
5
1
9
`
:
 
H
a
s
h
e
s
 
t
h
e
 
s
e
e
d
 
t
o
 
g
e
t
 
t
h
e
 
s
e
c
r
e
t
 
k
e
y
,
 
d
e
r
i
v
e
s
 
t
h
e
 
p
u
b
l
i
c
 
k
e
y
,
 
a
n
d
 
r
e
t
u
r
n
s
 
t
h
e
 
p
a
i
r
.


 
 
-
 
A
l
l
 
s
e
n
s
i
t
i
v
e
 
b
u
f
f
e
r
s
 
a
r
e
 
s
e
c
u
r
e
l
y
 
e
r
a
s
e
d
 
a
f
t
e
r
 
u
s
e
.




-
 
*
*
r
a
n
d
o
m
K
e
y
P
a
i
r
(
K
e
y
T
y
p
e
 
t
y
p
e
)
:
*
*
 
 


 
 
-
 
G
e
n
e
r
a
t
e
s
 
a
 
r
a
n
d
o
m
 
s
e
c
r
e
t
 
k
e
y
 
u
s
i
n
g
 
`
r
a
n
d
o
m
S
e
c
r
e
t
K
e
y
(
)
`
.


 
 
-
 
D
e
r
i
v
e
s
 
t
h
e
 
c
o
r
r
e
s
p
o
n
d
i
n
g
 
p
u
b
l
i
c
 
k
e
y
.


 
 
-
 
R
e
t
u
r
n
s
 
b
o
t
h
 
a
s
 
a
 
p
a
i
r
.




#
#
#
 
K
e
y
 
E
n
c
o
d
i
n
g
/
D
e
c
o
d
i
n
g
 
(
B
a
s
e
5
8
)




-
 
*
*
t
o
B
a
s
e
5
8
(
T
o
k
e
n
T
y
p
e
 
t
y
p
e
,
 
P
u
b
l
i
c
K
e
y
/
S
e
c
r
e
t
K
e
y
 
c
o
n
s
t
&
 
k
)
:
*
*
 
 


 
 
-
 
E
n
c
o
d
e
s
 
t
h
e
 
k
e
y
 
b
y
t
e
s
 
i
n
t
o
 
a
 
B
a
s
e
5
8
 
s
t
r
i
n
g
 
w
i
t
h
 
a
 
t
y
p
e
 
p
r
e
f
i
x
 
a
n
d
 
c
h
e
c
k
s
u
m
.


 
 
-
 
U
s
e
s
 
`
e
n
c
o
d
e
B
a
s
e
5
8
T
o
k
e
n
`
.




-
 
*
*
p
a
r
s
e
B
a
s
e
5
8
(
T
o
k
e
n
T
y
p
e
 
t
y
p
e
,
 
s
t
d
:
:
s
t
r
i
n
g
 
c
o
n
s
t
&
 
s
)
:
*
*
 
 


 
 
-
 
D
e
c
o
d
e
s
 
a
 
B
a
s
e
5
8
 
s
t
r
i
n
g
,
 
c
h
e
c
k
s
 
t
h
e
 
t
y
p
e
 
a
n
d
 
c
h
e
c
k
s
u
m
,
 
a
n
d
 
c
o
n
s
t
r
u
c
t
s
 
a
 
k
e
y
 
o
b
j
e
c
t
 
i
f
 
v
a
l
i
d
.


 
 
-
 
R
e
t
u
r
n
s
 
`
s
t
d
:
:
o
p
t
i
o
n
a
l
<
P
u
b
l
i
c
K
e
y
/
S
e
c
r
e
t
K
e
y
>
`
.




-
 
*
*
e
n
c
o
d
e
B
a
s
e
5
8
T
o
k
e
n
:
*
*
 
 


 
 
-
 
C
o
n
s
t
r
u
c
t
s
 
a
 
b
u
f
f
e
r
:
 
1
-
b
y
t
e
 
t
y
p
e
 
p
r
e
f
i
x
,
 
k
e
y
 
d
a
t
a
,
 
4
-
b
y
t
e
 
c
h
e
c
k
s
u
m
.


 
 
-
 
B
a
s
e
5
8
-
e
n
c
o
d
e
s
 
t
h
e
 
b
u
f
f
e
r
.




-
 
*
*
d
e
c
o
d
e
B
a
s
e
5
8
T
o
k
e
n
:
*
*
 
 


 
 
-
 
D
e
c
o
d
e
s
 
a
 
B
a
s
e
5
8
 
s
t
r
i
n
g
,
 
c
h
e
c
k
s
 
t
h
e
 
t
y
p
e
 
a
n
d
 
c
h
e
c
k
s
u
m
,
 
a
n
d
 
r
e
t
u
r
n
s
 
t
h
e
 
r
a
w
 
b
y
t
e
s
.




#
#
#
 
R
F
C
1
7
5
1
 
M
n
e
m
o
n
i
c
 
E
n
c
o
d
i
n
g




-
 
*
*
g
e
t
E
n
g
l
i
s
h
F
r
o
m
K
e
y
(
s
t
d
:
:
s
t
r
i
n
g
&
 
s
t
r
H
u
m
a
n
,
 
s
t
d
:
:
s
t
r
i
n
g
 
c
o
n
s
t
&
 
s
t
r
K
e
y
)
:
*
*
 
 


 
 
-
 
C
o
n
v
e
r
t
s
 
a
 
1
6
-
b
y
t
e
 
b
i
n
a
r
y
 
k
e
y
 
i
n
t
o
 
a
 
1
2
-
w
o
r
d
 
h
u
m
a
n
-
r
e
a
d
a
b
l
e
 
s
t
r
i
n
g
 
u
s
i
n
g
 
t
h
e
 
R
F
C
 
1
7
5
1
 
w
o
r
d
 
l
i
s
t
.


 
 
-
 
S
p
l
i
t
s
 
t
h
e
 
k
e
y
 
i
n
t
o
 
t
w
o
 
8
-
b
y
t
e
 
h
a
l
v
e
s
,
 
e
n
c
o
d
e
s
 
e
a
c
h
 
t
o
 
6
 
w
o
r
d
s
,
 
a
n
d
 
j
o
i
n
s
 
t
h
e
m
.




-
 
*
*
g
e
t
K
e
y
F
r
o
m
E
n
g
l
i
s
h
(
s
t
d
:
:
s
t
r
i
n
g
&
 
s
t
r
K
e
y
,
 
s
t
d
:
:
s
t
r
i
n
g
 
c
o
n
s
t
&
 
s
t
r
H
u
m
a
n
)
:
*
*
 
 


 
 
-
 
C
o
n
v
e
r
t
s
 
a
 
1
2
-
w
o
r
d
 
m
n
e
m
o
n
i
c
 
b
a
c
k
 
i
n
t
o
 
a
 
1
6
-
b
y
t
e
 
b
i
n
a
r
y
 
k
e
y
.


 
 
-
 
S
p
l
i
t
s
 
t
h
e
 
p
h
r
a
s
e
,
 
d
e
c
o
d
e
s
 
e
a
c
h
 
g
r
o
u
p
 
o
f
 
6
 
w
o
r
d
s
,
 
a
n
d
 
c
o
n
c
a
t
e
n
a
t
e
s
.




-
 
*
*
g
e
t
W
o
r
d
F
r
o
m
B
l
o
b
(
v
o
i
d
 
c
o
n
s
t
*
 
b
l
o
b
,
 
s
i
z
e
_
t
 
b
y
t
e
s
)
:
*
*
 
 


 
 
-
 
H
a
s
h
e
s
 
a
 
b
i
n
a
r
y
 
b
l
o
b
 
a
n
d
 
m
a
p
s
 
i
t
 
t
o
 
a
 
s
i
n
g
l
e
 
w
o
r
d
 
f
r
o
m
 
t
h
e
 
R
F
C
1
7
5
1
 
d
i
c
t
i
o
n
a
r
y
.




-
-
-




#
#
 
R
a
n
d
o
m
 
N
u
m
b
e
r
 
G
e
n
e
r
a
t
i
o
n




#
#
#
 
c
s
p
r
n
g
_
e
n
g
i
n
e
 
a
n
d
 
c
r
y
p
t
o
_
p
r
n
g




-
 
*
*
c
s
p
r
n
g
_
e
n
g
i
n
e
:
*
*
 
 


 
 
-
 
W
r
a
p
s
 
O
p
e
n
S
S
L
'
s
 
r
a
n
d
o
m
 
n
u
m
b
e
r
 
g
e
n
e
r
a
t
i
o
n
.


 
 
-
 
S
e
e
d
s
 
w
i
t
h
 
s
y
s
t
e
m
 
e
n
t
r
o
p
y
 
(
`
R
A
N
D
_
p
o
l
l
`
)
.


 
 
-
 
P
r
o
v
i
d
e
s
 
t
h
r
e
a
d
-
s
a
f
e
 
m
e
t
h
o
d
s
 
t
o
 
f
i
l
l
 
b
u
f
f
e
r
s
 
w
i
t
h
 
r
a
n
d
o
m
 
b
y
t
e
s
 
(
`
R
A
N
D
_
b
y
t
e
s
`
)
.


 
 
-
 
C
a
n
 
m
i
x
 
a
d
d
i
t
i
o
n
a
l
 
e
n
t
r
o
p
y
 
f
r
o
m
 
`
s
t
d
:
:
r
a
n
d
o
m
_
d
e
v
i
c
e
`
 
o
r
 
u
s
e
r
-
s
u
p
p
l
i
e
d
 
b
u
f
f
e
r
s
 
(
`
R
A
N
D
_
a
d
d
`
)
.


 
 
-
 
T
h
r
o
w
s
 
o
n
 
f
a
i
l
u
r
e
 
t
o
 
s
e
e
d
 
o
r
 
i
n
s
u
f
f
i
c
i
e
n
t
 
e
n
t
r
o
p
y
.


 
 
-
 
S
i
n
g
l
e
t
o
n
 
i
n
s
t
a
n
c
e
 
p
r
o
v
i
d
e
d
 
b
y
 
`
c
r
y
p
t
o
_
p
r
n
g
(
)
`
.




-
 
*
*
r
a
n
d
o
m
S
e
c
r
e
t
K
e
y
(
)
*
*
 
u
s
e
s
 
t
h
i
s
 
e
n
g
i
n
e
 
t
o
 
g
e
n
e
r
a
t
e
 
s
e
c
u
r
e
 
r
a
n
d
o
m
 
k
e
y
s
.




-
-
-




#
#
 
H
a
s
h
 
F
u
n
c
t
i
o
n
s




#
#
#
 
S
H
A
-
2
5
6
,
 
S
H
A
-
5
1
2
,
 
R
I
P
E
M
D
-
1
6
0




-
 
*
*
o
p
e
n
s
s
l
_
s
h
a
2
5
6
_
h
a
s
h
e
r
:
*
*
 
 


 
 
-
 
W
r
a
p
s
 
O
p
e
n
S
S
L
'
s
 
S
H
A
-
2
5
6
 
c
o
n
t
e
x
t
.


 
 
-
 
`
o
p
e
r
a
t
o
r
(
)
(
v
o
i
d
 
c
o
n
s
t
*
 
d
a
t
a
,
 
s
t
d
:
:
s
i
z
e
_
t
 
s
i
z
e
)
`
:
 
F
e
e
d
s
 
d
a
t
a
 
i
n
t
o
 
t
h
e
 
h
a
s
h
.


 
 
-
 
`
o
p
e
r
a
t
o
r
 
r
e
s
u
l
t
_
t
y
p
e
(
)
`
:
 
F
i
n
a
l
i
z
e
s
 
a
n
d
 
r
e
t
u
r
n
s
 
t
h
e
 
3
2
-
b
y
t
e
 
d
i
g
e
s
t
.




-
 
*
*
o
p
e
n
s
s
l
_
s
h
a
5
1
2
_
h
a
s
h
e
r
:
*
*
 
 


 
 
-
 
S
a
m
e
 
a
s
 
a
b
o
v
e
,
 
b
u
t
 
f
o
r
 
S
H
A
-
5
1
2
 
(
6
4
-
b
y
t
e
 
d
i
g
e
s
t
)
.




-
 
*
*
o
p
e
n
s
s
l
_
r
i
p
e
m
d
1
6
0
_
h
a
s
h
e
r
:
*
*
 
 


 
 
-
 
S
a
m
e
 
a
s
 
a
b
o
v
e
,
 
b
u
t
 
f
o
r
 
R
I
P
E
M
D
-
1
6
0
 
(
2
0
-
b
y
t
e
 
d
i
g
e
s
t
)
.




#
#
#
 
s
h
a
5
1
2
H
a
l
f
 
a
n
d
 
r
i
p
e
s
h
a
_
h
a
s
h
e
r




-
 
*
*
s
h
a
5
1
2
_
h
a
l
f
_
h
a
s
h
e
r
:
*
*
 
 


 
 
-
 
F
e
e
d
s
 
d
a
t
a
 
i
n
t
o
 
S
H
A
-
5
1
2
,
 
t
h
e
n
 
r
e
t
u
r
n
s
 
t
h
e
 
f
i
r
s
t
 
3
2
 
b
y
t
e
s
 
(
2
5
6
 
b
i
t
s
)
 
a
s
 
a
 
`
u
i
n
t
2
5
6
`
.


 
 
-
 
U
s
e
d
 
f
o
r
 
t
r
a
n
s
a
c
t
i
o
n
/
l
e
d
g
e
r
 
h
a
s
h
e
s
 
a
n
d
 
k
e
y
 
d
e
r
i
v
a
t
i
o
n
.




-
 
*
*
s
h
a
5
1
2
H
a
l
f
(
A
r
g
s
.
.
.
)
:
*
*
 
 


 
 
-
 
H
a
s
h
e
s
 
t
h
e
 
p
r
o
v
i
d
e
d
 
a
r
g
u
m
e
n
t
s
 
u
s
i
n
g
 
`
s
h
a
5
1
2
_
h
a
l
f
_
h
a
s
h
e
r
`
.




-
 
*
*
r
i
p
e
s
h
a
_
h
a
s
h
e
r
:
*
*
 
 


 
 
-
 
F
e
e
d
s
 
d
a
t
a
 
i
n
t
o
 
S
H
A
-
2
5
6
,
 
t
h
e
n
 
h
a
s
h
e
s
 
t
h
e
 
r
e
s
u
l
t
 
w
i
t
h
 
R
I
P
E
M
D
-
1
6
0
.


 
 
-
 
U
s
e
d
 
f
o
r
 
a
d
d
r
e
s
s
 
d
e
r
i
v
a
t
i
o
n
 
(
h
a
s
h
1
6
0
)
.




-
-
-




#
#
 
D
i
g
i
t
a
l
 
S
i
g
n
a
t
u
r
e
s




#
#
#
 
S
i
g
n
i
n
g
 
a
n
d
 
V
e
r
i
f
y
i
n
g




-
 
*
*
s
i
g
n
(
P
u
b
l
i
c
K
e
y
 
c
o
n
s
t
&
 
p
k
,
 
S
e
c
r
e
t
K
e
y
 
c
o
n
s
t
&
 
s
k
,
 
S
l
i
c
e
 
c
o
n
s
t
&
 
m
)
:
*
*
 
 


 
 
-
 
D
e
t
e
r
m
i
n
e
s
 
k
e
y
 
t
y
p
e
 
f
r
o
m
 
t
h
e
 
p
u
b
l
i
c
 
k
e
y
.


 
 
-
 
F
o
r
 
`
e
d
2
5
5
1
9
`
:


 
 
 
 
-
 
C
a
l
l
s
 
`
e
d
2
5
5
1
9
_
s
i
g
n
`
 
w
i
t
h
 
t
h
e
 
m
e
s
s
a
g
e
,
 
s
e
c
r
e
t
 
k
e
y
,
 
a
n
d
 
p
u
b
l
i
c
 
k
e
y
.


 
 
 
 
-
 
R
e
t
u
r
n
s
 
a
 
6
4
-
b
y
t
e
 
s
i
g
n
a
t
u
r
e
.


 
 
-
 
F
o
r
 
`
s
e
c
p
2
5
6
k
1
`
:


 
 
 
 
-
 
H
a
s
h
e
s
 
t
h
e
 
m
e
s
s
a
g
e
 
w
i
t
h
 
`
s
h
a
5
1
2
_
h
a
l
f
_
h
a
s
h
e
r
`
.


 
 
 
 
-
 
C
a
l
l
s
 
`
s
e
c
p
2
5
6
k
1
_
e
c
d
s
a
_
s
i
g
n
`
 
w
i
t
h
 
t
h
e
 
d
i
g
e
s
t
 
a
n
d
 
s
e
c
r
e
t
 
k
e
y
.


 
 
 
 
-
 
S
e
r
i
a
l
i
z
e
s
 
t
h
e
 
s
i
g
n
a
t
u
r
e
 
i
n
 
D
E
R
 
f
o
r
m
a
t
.


 
 
 
 
-
 
R
e
t
u
r
n
s
 
t
h
e
 
D
E
R
-
e
n
c
o
d
e
d
 
s
i
g
n
a
t
u
r
e
.


 
 
-
 
T
h
r
o
w
s
 
o
n
 
e
r
r
o
r
 
o
r
 
u
n
k
n
o
w
n
 
k
e
y
 
t
y
p
e
.




-
 
*
*
s
i
g
n
D
i
g
e
s
t
(
P
u
b
l
i
c
K
e
y
 
c
o
n
s
t
&
 
p
k
,
 
S
e
c
r
e
t
K
e
y
 
c
o
n
s
t
&
 
s
k
,
 
u
i
n
t
2
5
6
 
c
o
n
s
t
&
 
d
i
g
e
s
t
)
:
*
*
 
 


 
 
-
 
O
n
l
y
 
s
u
p
p
o
r
t
s
 
`
s
e
c
p
2
5
6
k
1
`
.


 
 
-
 
S
i
g
n
s
 
a
 
3
2
-
b
y
t
e
 
d
i
g
e
s
t
 
u
s
i
n
g
 
`
s
e
c
p
2
5
6
k
1
_
e
c
d
s
a
_
s
i
g
n
`
.


 
 
-
 
S
e
r
i
a
l
i
z
e
s
 
t
h
e
 
s
i
g
n
a
t
u
r
e
 
i
n
 
D
E
R
 
f
o
r
m
a
t
.


 
 
-
 
R
e
t
u
r
n
s
 
t
h
e
 
s
i
g
n
a
t
u
r
e
 
a
s
 
a
 
`
B
u
f
f
e
r
`
.


 
 
-
 
T
h
r
o
w
s
 
i
f
 
t
h
e
 
k
e
y
 
t
y
p
e
 
i
s
 
n
o
t
 
`
s
e
c
p
2
5
6
k
1
`
.




-
 
*
*
S
T
T
x
:
:
s
i
g
n
(
P
u
b
l
i
c
K
e
y
 
c
o
n
s
t
&
 
p
u
b
l
i
c
K
e
y
,
 
S
e
c
r
e
t
K
e
y
 
c
o
n
s
t
&
 
s
e
c
r
e
t
K
e
y
)
:
*
*
 
 


 
 
-
 
S
e
r
i
a
l
i
z
e
s
 
t
h
e
 
t
r
a
n
s
a
c
t
i
o
n
 
f
o
r
 
s
i
g
n
i
n
g
.


 
 
-
 
C
a
l
l
s
 
`
r
i
p
p
l
e
:
:
s
i
g
n
`
 
t
o
 
g
e
n
e
r
a
t
e
 
t
h
e
 
s
i
g
n
a
t
u
r
e
.


 
 
-
 
A
t
t
a
c
h
e
s
 
t
h
e
 
s
i
g
n
a
t
u
r
e
 
t
o
 
t
h
e
 
t
r
a
n
s
a
c
t
i
o
n
.




-
-
-




#
#
 
S
e
c
u
r
e
 
M
e
m
o
r
y
 
E
r
a
s
u
r
e




-
 
*
*
s
e
c
u
r
e
_
e
r
a
s
e
(
v
o
i
d
*
 
d
e
s
t
,
 
s
t
d
:
:
s
i
z
e
_
t
 
b
y
t
e
s
)
:
*
*
 
 


 
 
-
 
C
a
l
l
s
 
`
O
P
E
N
S
S
L
_
c
l
e
a
n
s
e
`
 
t
o
 
s
e
c
u
r
e
l
y
 
o
v
e
r
w
r
i
t
e
 
m
e
m
o
r
y
.


 
 
-
 
U
s
e
d
 
i
n
 
d
e
s
t
r
u
c
t
o
r
s
 
a
n
d
 
a
f
t
e
r
 
h
a
n
d
l
i
n
g
 
s
e
n
s
i
t
i
v
e
 
d
a
t
a
.




-
-
-




#
#
 
S
S
L
/
T
L
S
 
C
o
n
t
e
x
t
 
a
n
d
 
H
a
n
d
s
h
a
k
e
 
S
e
c
u
r
i
t
y




#
#
#
 
m
a
k
e
_
S
S
L
C
o
n
t
e
x
t
 
a
n
d
 
m
a
k
e
_
S
S
L
C
o
n
t
e
x
t
A
u
t
h
e
d




-
 
*
*
m
a
k
e
_
S
S
L
C
o
n
t
e
x
t
(
c
i
p
h
e
r
L
i
s
t
)
:
*
*
 
 


 
 
-
 
C
r
e
a
t
e
s
 
a
 
n
e
w
 
S
S
L
 
c
o
n
t
e
x
t
 
f
o
r
 
a
n
o
n
y
m
o
u
s
 
c
o
n
n
e
c
t
i
o
n
s
.


 
 
-
 
G
e
n
e
r
a
t
e
s
 
e
p
h
e
m
e
r
a
l
 
k
e
y
s
 
a
n
d
 
a
 
s
e
l
f
-
s
i
g
n
e
d
 
c
e
r
t
i
f
i
c
a
t
e
.


 
 
-
 
D
i
s
a
b
l
e
s
 
p
e
e
r
 
v
e
r
i
f
i
c
a
t
i
o
n
.




-
 
*
*
m
a
k
e
_
S
S
L
C
o
n
t
e
x
t
A
u
t
h
e
d
(
k
e
y
F
i
l
e
,
 
c
e
r
t
F
i
l
e
,
 
c
h
a
i
n
F
i
l
e
,
 
c
i
p
h
e
r
L
i
s
t
)
:
*
*
 
 


 
 
-
 
C
r
e
a
t
e
s
 
a
 
n
e
w
 
S
S
L
 
c
o
n
t
e
x
t
 
f
o
r
 
a
u
t
h
e
n
t
i
c
a
t
e
d
 
c
o
n
n
e
c
t
i
o
n
s
.


 
 
-
 
L
o
a
d
s
 
t
h
e
 
p
r
o
v
i
d
e
d
 
p
r
i
v
a
t
e
 
k
e
y
,
 
c
e
r
t
i
f
i
c
a
t
e
,
 
a
n
d
 
c
h
a
i
n
 
f
i
l
e
s
.


 
 
-
 
V
e
r
i
f
i
e
s
 
t
h
e
 
p
r
i
v
a
t
e
 
k
e
y
 
m
a
t
c
h
e
s
 
t
h
e
 
c
e
r
t
i
f
i
c
a
t
e
.




#
#
#
 
O
v
e
r
l
a
y
 
H
a
n
d
s
h
a
k
e
 
a
n
d
 
M
I
T
M
 
P
r
o
t
e
c
t
i
o
n




-
 
*
*
b
u
i
l
d
H
a
n
d
s
h
a
k
e
:
*
*
 
 


 
 
-
 
C
o
n
s
t
r
u
c
t
s
 
H
T
T
P
 
h
e
a
d
e
r
s
 
f
o
r
 
t
h
e
 
o
v
e
r
l
a
y
 
h
a
n
d
s
h
a
k
e
.


 
 
-
 
I
n
c
l
u
d
e
s
:


 
 
 
 
-
 
N
e
t
w
o
r
k
 
I
D
 
(
i
f
 
p
r
e
s
e
n
t
)


 
 
 
 
-
 
N
e
t
w
o
r
k
 
T
i
m
e


 
 
 
 
-
 
N
o
d
e
'
s
 
p
u
b
l
i
c
 
k
e
y
 
(
B
a
s
e
5
8
-
e
n
c
o
d
e
d
)


 
 
 
 
-
 
S
e
s
s
i
o
n
 
s
i
g
n
a
t
u
r
e
:
 
 


 
 
 
 
 
 
-
 
S
i
g
n
s
 
t
h
e
 
s
e
s
s
i
o
n
'
s
 
u
n
i
q
u
e
 
f
i
n
g
e
r
p
r
i
n
t
 
(
`
s
h
a
r
e
d
V
a
l
u
e
`
)
 
w
i
t
h
 
t
h
e
 
n
o
d
e
'
s
 
p
r
i
v
a
t
e
 
k
e
y
 
u
s
i
n
g
 
`
s
i
g
n
D
i
g
e
s
t
`
.


 
 
 
 
 
 
-
 
E
n
c
o
d
e
s
 
t
h
e
 
s
i
g
n
a
t
u
r
e
 
i
n
 
b
a
s
e
6
4
.


 
 
 
 
-
 
I
n
s
t
a
n
c
e
 
C
o
o
k
i
e


 
 
-
 
T
h
i
s
 
p
r
o
c
e
s
s
 
b
i
n
d
s
 
t
h
e
 
S
S
L
/
T
L
S
 
s
e
s
s
i
o
n
 
t
o
 
t
h
e
 
n
o
d
e
'
s
 
i
d
e
n
t
i
t
y
,
 
p
r
e
v
e
n
t
i
n
g
 
M
I
T
M
 
a
t
t
a
c
k
s
 
b
y
 
e
n
s
u
r
i
n
g
 
b
o
t
h
 
e
n
d
p
o
i
n
t
s
 
c
a
n
 
p
r
o
v
e
 
p
o
s
s
e
s
s
i
o
n
 
o
f
 
t
h
e
i
r
 
p
r
i
v
a
t
e
 
k
e
y
s
 
a
n
d
 
a
g
r
e
e
 
o
n
 
t
h
e
 
s
e
s
s
i
o
n
 
f
i
n
g
e
r
p
r
i
n
t
.




-
 
*
*
M
I
T
M
 
A
t
t
a
c
k
 
P
r
e
v
e
n
t
i
o
n
:
*
*
 
 


 
 
-
 
I
f
 
a
n
 
a
t
t
a
c
k
e
r
 
e
s
t
a
b
l
i
s
h
e
s
 
t
w
o
 
s
e
p
a
r
a
t
e
 
S
S
L
 
s
e
s
s
i
o
n
s
,
 
t
h
e
 
f
i
n
g
e
r
p
r
i
n
t
s
 
w
i
l
l
 
d
i
f
f
e
r
 
a
n
d
 
t
h
e
 
a
t
t
a
c
k
e
r
 
c
a
n
n
o
t
 
s
i
g
n
 
w
i
t
h
 
t
h
e
 
c
o
r
r
e
c
t
 
p
r
i
v
a
t
e
 
k
e
y
.
 
B
o
t
h
 
e
n
d
p
o
i
n
t
s
 
w
i
l
l
 
d
e
t
e
c
t
 
t
h
e
 
a
t
t
a
c
k
 
a
n
d
 
c
l
o
s
e
 
t
h
e
 
c
o
n
n
e
c
t
i
o
n
.




-
-
-




#
#
 
C
o
m
p
o
n
e
n
t
 
I
n
t
e
r
a
c
t
i
o
n
s




-
 
*
*
K
e
y
 
G
e
n
e
r
a
t
i
o
n
:
*
*
 
 


 
 
-
 
U
s
e
s
 
s
e
c
u
r
e
 
r
a
n
d
o
m
 
n
u
m
b
e
r
 
g
e
n
e
r
a
t
i
o
n
 
(
`
c
s
p
r
n
g
_
e
n
g
i
n
e
`
)
 
f
o
r
 
e
n
t
r
o
p
y
.


 
 
-
 
K
e
y
s
 
a
r
e
 
e
n
c
o
d
e
d
/
d
e
c
o
d
e
d
 
f
o
r
 
s
t
o
r
a
g
e
 
a
n
d
 
t
r
a
n
s
m
i
s
s
i
o
n
 
u
s
i
n
g
 
B
a
s
e
5
8
 
a
n
d
 
R
F
C
1
7
5
1
 
m
n
e
m
o
n
i
c
s
.




-
 
*
*
S
i
g
n
i
n
g
:
*
*
 
 


 
 
-
 
T
r
a
n
s
a
c
t
i
o
n
s
 
a
n
d
 
p
r
o
t
o
c
o
l
 
m
e
s
s
a
g
e
s
 
a
r
e
 
s
e
r
i
a
l
i
z
e
d
,
 
h
a
s
h
e
d
,
 
a
n
d
 
s
i
g
n
e
d
 
u
s
i
n
g
 
t
h
e
 
a
p
p
r
o
p
r
i
a
t
e
 
k
e
y
 
t
y
p
e
.


 
 
-
 
S
i
g
n
a
t
u
r
e
s
 
a
r
e
 
v
e
r
i
f
i
e
d
 
b
y
 
p
e
e
r
s
 
u
s
i
n
g
 
t
h
e
 
p
u
b
l
i
c
 
k
e
y
.




-
 
*
*
H
a
s
h
i
n
g
:
*
*
 
 


 
 
-
 
U
s
e
d
 
f
o
r
 
a
d
d
r
e
s
s
 
d
e
r
i
v
a
t
i
o
n
,
 
t
r
a
n
s
a
c
t
i
o
n
/
l
e
d
g
e
r
 
I
D
s
,
 
a
n
d
 
c
h
e
c
k
s
u
m
s
.




-
 
*
*
S
S
L
/
T
L
S
:
*
*
 
 


 
 
-
 
S
e
c
u
r
e
 
c
o
m
m
u
n
i
c
a
t
i
o
n
 
i
s
 
e
s
t
a
b
l
i
s
h
e
d
 
u
s
i
n
g
 
S
S
L
 
c
o
n
t
e
x
t
s
.


 
 
-
 
O
v
e
r
l
a
y
 
h
a
n
d
s
h
a
k
e
 
c
r
y
p
t
o
g
r
a
p
h
i
c
a
l
l
y
 
b
i
n
d
s
 
t
h
e
 
s
e
s
s
i
o
n
 
t
o
 
n
o
d
e
 
i
d
e
n
t
i
t
i
e
s
.




-
 
*
*
S
e
c
u
r
i
t
y
:
*
*
 
 


 
 
-
 
A
l
l
 
s
e
n
s
i
t
i
v
e
 
d
a
t
a
 
i
s
 
s
e
c
u
r
e
l
y
 
e
r
a
s
e
d
 
f
r
o
m
 
m
e
m
o
r
y
 
a
f
t
e
r
 
u
s
e
.


 
 
-
 
A
l
l
 
c
r
y
p
t
o
g
r
a
p
h
i
c
 
o
p
e
r
a
t
i
o
n
s
 
u
s
e
 
w
e
l
l
-
e
s
t
a
b
l
i
s
h
e
d
,
 
p
e
e
r
-
r
e
v
i
e
w
e
d
 
a
l
g
o
r
i
t
h
m
s
 
a
n
d
 
l
i
b
r
a
r
i
e
s
 
(
O
p
e
n
S
S
L
,
 
s
e
c
p
2
5
6
k
1
,
 
e
d
2
5
5
1
9
)
.




-
-
-




#
#
 
E
r
r
o
r
 
H
a
n
d
l
i
n
g




-
 
F
u
n
c
t
i
o
n
s
 
s
u
c
h
 
a
s
 
`
S
e
c
r
e
t
K
e
y
`
 
c
o
n
s
t
r
u
c
t
o
r
s
,
 
`
g
e
n
e
r
a
t
e
S
e
c
r
e
t
K
e
y
`
,
 
`
d
e
r
i
v
e
D
e
t
e
r
m
i
n
i
s
t
i
c
R
o
o
t
K
e
y
`
,
 
a
n
d
 
c
r
y
p
t
o
g
r
a
p
h
i
c
 
o
p
e
r
a
t
i
o
n
s
 
*
*
t
h
r
o
w
 
e
x
c
e
p
t
i
o
n
s
*
*
 
(
e
.
g
.
,
 
`
s
t
d
:
:
r
u
n
t
i
m
e
_
e
r
r
o
r
`
,
 
`
L
o
g
i
c
E
r
r
o
r
`
)
 
o
n
 
e
r
r
o
r
s
 
s
u
c
h
 
a
s
 
i
n
v
a
l
i
d
 
k
e
y
 
s
i
z
e
,
 
u
n
k
n
o
w
n
 
k
e
y
 
t
y
p
e
,
 
o
r
 
c
r
y
p
t
o
g
r
a
p
h
i
c
 
f
a
i
l
u
r
e
s
.


-
 
F
u
n
c
t
i
o
n
s
 
t
h
a
t
 
d
e
c
o
d
e
 
o
r
 
p
a
r
s
e
 
(
e
.
g
.
,
 
`
p
a
r
s
e
B
a
s
e
5
8
`
)
 
r
e
t
u
r
n
 
`
s
t
d
:
:
o
p
t
i
o
n
a
l
`
 
t
o
 
i
n
d
i
c
a
t
e
 
f
a
i
l
u
r
e
.


-
 
I
f
 
s
i
g
n
a
t
u
r
e
 
v
e
r
i
f
i
c
a
t
i
o
n
 
f
a
i
l
s
 
d
u
r
i
n
g
 
h
a
n
d
s
h
a
k
e
,
 
t
h
e
 
c
o
n
n
e
c
t
i
o
n
 
*
*
M
U
S
T
*
*
 
b
e
 
d
r
o
p
p
e
d
.


-
 
I
f
 
r
a
n
d
o
m
 
n
u
m
b
e
r
 
g
e
n
e
r
a
t
i
o
n
 
f
a
i
l
s
 
t
o
 
s
e
e
d
 
o
r
 
p
r
o
v
i
d
e
 
s
u
f
f
i
c
i
e
n
t
 
e
n
t
r
o
p
y
,
 
a
n
 
e
x
c
e
p
t
i
o
n
 
i
s
 
t
h
r
o
w
n
.




-
-
-




#
#
 
S
u
p
p
o
r
t
e
d
 
K
e
y
 
T
y
p
e
s
 
a
n
d
 
A
l
g
o
r
i
t
h
m
s




-
 
*
*
S
u
p
p
o
r
t
e
d
 
K
e
y
 
T
y
p
e
s
:
*
*
 
 


 
 
-
 
`
e
d
2
5
5
1
9
`


 
 
-
 
`
s
e
c
p
2
5
6
k
1
`


-
 
*
*
S
u
m
m
a
r
y
 
T
a
b
l
e
:
*
*




|
 
K
e
y
 
T
y
p
e
 
 
 
|
 
U
s
e
 
C
a
s
e
s
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
|
 
S
u
p
p
o
r
t
e
d
 
O
p
e
r
a
t
i
o
n
s
 
 
 
 
 
 
 
 
 
|


|
-
-
-
-
-
-
-
-
-
-
-
-
|
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
|
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
|


|
 
e
d
2
5
5
1
9
 
 
 
 
|
 
A
c
c
o
u
n
t
 
k
e
y
s
,
 
s
i
g
n
i
n
g
 
 
 
|
 
K
e
y
 
g
e
n
e
r
a
t
i
o
n
,
 
s
i
g
n
i
n
g
 
 
 
 
 
|


|
 
s
e
c
p
2
5
6
k
1
 
 
|
 
N
o
d
e
 
i
d
e
n
t
i
t
y
,
 
s
i
g
n
i
n
g
 
 
|
 
K
e
y
 
g
e
n
e
r
a
t
i
o
n
,
 
s
i
g
n
i
n
g
 
 
 
 
 
|




-
 
N
o
 
o
t
h
e
r
 
k
e
y
 
t
y
p
e
s
 
a
r
e
 
s
u
p
p
o
r
t
e
d
 
a
s
 
p
e
r
 
t
h
e
 
p
r
o
v
i
d
e
d
 
i
n
f
o
r
m
a
t
i
o
n
.




-
-
-




#
#
 
K
e
y
 
F
o
r
m
a
t
 
D
e
t
a
i
l
s




-
 
*
*
B
a
s
e
5
8
 
E
n
c
o
d
i
n
g
:
*
*


 
 
-
 
K
e
y
s
 
a
r
e
 
e
n
c
o
d
e
d
 
a
s
 
B
a
s
e
5
8
 
s
t
r
i
n
g
s
 
w
i
t
h
:


 
 
 
 
-
 
1
-
b
y
t
e
 
t
y
p
e
 
p
r
e
f
i
x


 
 
 
 
-
 
K
e
y
 
d
a
t
a


 
 
 
 
-
 
4
-
b
y
t
e
 
c
h
e
c
k
s
u
m
 
(
f
i
r
s
t
 
4
 
b
y
t
e
s
 
o
f
 
d
o
u
b
l
e
 
S
H
A
-
2
5
6
)


 
 
-
 
D
e
c
o
d
i
n
g
 
c
h
e
c
k
s
 
t
h
e
 
p
r
e
f
i
x
 
a
n
d
 
c
h
e
c
k
s
u
m
 
b
e
f
o
r
e
 
c
o
n
s
t
r
u
c
t
i
n
g
 
t
h
e
 
k
e
y
 
o
b
j
e
c
t
.




-
 
*
*
R
F
C
1
7
5
1
 
M
n
e
m
o
n
i
c
:
*
*


 
 
-
 
1
6
-
b
y
t
e
 
b
i
n
a
r
y
 
k
e
y
s
 
a
r
e
 
e
n
c
o
d
e
d
 
a
s
 
1
2
-
w
o
r
d
 
p
h
r
a
s
e
s
 
u
s
i
n
g
 
t
h
e
 
R
F
C
1
7
5
1
 
w
o
r
d
 
l
i
s
t
.


 
 
-
 
T
h
e
 
k
e
y
 
i
s
 
s
p
l
i
t
 
i
n
t
o
 
t
w
o
 
8
-
b
y
t
e
 
h
a
l
v
e
s
,
 
e
a
c
h
 
e
n
c
o
d
e
d
 
t
o
 
6
 
w
o
r
d
s
.




-
 
*
*
P
u
b
l
i
c
K
e
y
:
*
*
 
3
3
 
b
y
t
e
s
 
(
c
o
m
p
r
e
s
s
e
d
)


-
 
*
*
S
e
c
r
e
t
K
e
y
:
*
*
 
3
2
 
b
y
t
e
s




-
-
-




#
#
 
T
h
r
e
a
d
 
S
a
f
e
t
y




-
 
*
*
c
s
p
r
n
g
_
e
n
g
i
n
e
*
*
 
i
s
 
e
x
p
l
i
c
i
t
l
y
 
d
e
s
c
r
i
b
e
d
 
a
s
 
t
h
r
e
a
d
-
s
a
f
e
.


-
 
N
o
 
e
x
p
l
i
c
i
t
 
t
h
r
e
a
d
 
s
a
f
e
t
y
 
g
u
a
r
a
n
t
e
e
s
 
a
r
e
 
s
t
a
t
e
d
 
f
o
r
 
o
t
h
e
r
 
c
r
y
p
t
o
g
r
a
p
h
i
c
 
c
l
a
s
s
e
s
 
o
r
 
f
u
n
c
t
i
o
n
s
 
i
n
 
t
h
e
 
p
r
o
v
i
d
e
d
 
i
n
f
o
r
m
a
t
i
o
n
.




-
-
-




#
#
 
E
x
t
e
n
s
i
b
i
l
i
t
y




-
 
N
o
 
e
x
p
l
i
c
i
t
 
m
e
c
h
a
n
i
s
m
 
o
r
 
d
o
c
u
m
e
n
t
a
t
i
o
n
 
i
s
 
p
r
o
v
i
d
e
d
 
f
o
r
 
a
d
d
i
n
g
 
n
e
w
 
k
e
y
 
t
y
p
e
s
 
o
r
 
a
l
g
o
r
i
t
h
m
s
.


-
 
T
h
e
 
c
o
d
e
 
t
h
r
o
w
s
 
o
n
 
u
n
k
n
o
w
n
 
k
e
y
 
t
y
p
e
s
,
 
i
n
d
i
c
a
t
i
n
g
 
t
h
a
t
 
o
n
l
y
 
t
h
e
 
s
u
p
p
o
r
t
e
d
 
t
y
p
e
s
 
a
r
e
 
h
a
n
d
l
e
d
.




-
-
-




#
#
 
P
a
r
a
m
e
t
e
r
 
a
n
d
 
R
e
t
u
r
n
 
T
y
p
e
s




-
 
*
*
S
e
c
r
e
t
K
e
y
/
P
u
b
l
i
c
K
e
y
 
c
o
n
s
t
r
u
c
t
o
r
s
:
*
*
 
 


 
 
-
 
I
n
p
u
t
:
 
3
2
-
b
y
t
e
 
a
r
r
a
y
 
o
r
 
`
S
l
i
c
e
`
 
(
S
e
c
r
e
t
K
e
y
)
,
 
3
3
-
b
y
t
e
 
`
S
l
i
c
e
`
 
(
P
u
b
l
i
c
K
e
y
)


 
 
-
 
T
h
r
o
w
s
 
o
n
 
i
n
v
a
l
i
d
 
s
i
z
e




-
 
*
*
r
a
n
d
o
m
S
e
c
r
e
t
K
e
y
(
)
:
*
*
 
 


 
 
-
 
R
e
t
u
r
n
s
:
 
`
S
e
c
r
e
t
K
e
y
`




-
 
*
*
g
e
n
e
r
a
t
e
S
e
c
r
e
t
K
e
y
(
K
e
y
T
y
p
e
,
 
S
e
e
d
)
:
*
*
 
 


 
 
-
 
R
e
t
u
r
n
s
:
 
`
S
e
c
r
e
t
K
e
y
`


 
 
-
 
T
h
r
o
w
s
 
o
n
 
u
n
k
n
o
w
n
 
k
e
y
 
t
y
p
e




-
 
*
*
g
e
n
e
r
a
t
e
K
e
y
P
a
i
r
(
K
e
y
T
y
p
e
,
 
S
e
e
d
)
:
*
*
 
 


 
 
-
 
R
e
t
u
r
n
s
:
 
`
s
t
d
:
:
p
a
i
r
<
P
u
b
l
i
c
K
e
y
,
 
S
e
c
r
e
t
K
e
y
>
`




-
 
*
*
r
a
n
d
o
m
K
e
y
P
a
i
r
(
K
e
y
T
y
p
e
)
:
*
*
 
 


 
 
-
 
R
e
t
u
r
n
s
:
 
`
s
t
d
:
:
p
a
i
r
<
P
u
b
l
i
c
K
e
y
,
 
S
e
c
r
e
t
K
e
y
>
`




-
 
*
*
s
i
g
n
(
P
u
b
l
i
c
K
e
y
,
 
S
e
c
r
e
t
K
e
y
,
 
S
l
i
c
e
)
:
*
*
 
 


 
 
-
 
R
e
t
u
r
n
s
:
 
`
B
u
f
f
e
r
`
 
(
s
i
g
n
a
t
u
r
e
)


 
 
-
 
T
h
r
o
w
s
 
o
n
 
e
r
r
o
r
 
o
r
 
u
n
k
n
o
w
n
 
k
e
y
 
t
y
p
e




-
 
*
*
s
i
g
n
D
i
g
e
s
t
(
P
u
b
l
i
c
K
e
y
,
 
S
e
c
r
e
t
K
e
y
,
 
u
i
n
t
2
5
6
)
:
*
*
 
 


 
 
-
 
R
e
t
u
r
n
s
:
 
`
B
u
f
f
e
r
`
 
(
s
i
g
n
a
t
u
r
e
)


 
 
-
 
T
h
r
o
w
s
 
i
f
 
k
e
y
 
t
y
p
e
 
i
s
 
n
o
t
 
`
s
e
c
p
2
5
6
k
1
`




-
 
*
*
p
a
r
s
e
B
a
s
e
5
8
(
T
o
k
e
n
T
y
p
e
,
 
s
t
d
:
:
s
t
r
i
n
g
)
:
*
*
 
 


 
 
-
 
R
e
t
u
r
n
s
:
 
`
s
t
d
:
:
o
p
t
i
o
n
a
l
<
P
u
b
l
i
c
K
e
y
/
S
e
c
r
e
t
K
e
y
>
`




-
-
-




#
#
 
U
s
a
g
e
 
E
x
a
m
p
l
e
s




>
 
*
*
N
o
t
e
:
*
*
 
T
h
e
 
p
r
o
v
i
d
e
d
 
i
n
f
o
r
m
a
t
i
o
n
 
d
o
e
s
 
n
o
t
 
i
n
c
l
u
d
e
 
e
x
p
l
i
c
i
t
 
c
o
d
e
 
s
n
i
p
p
e
t
s
 
o
r
 
u
s
a
g
e
 
e
x
a
m
p
l
e
s
.
 
T
h
e
 
f
o
l
l
o
w
i
n
g
 
i
s
 
a
 
d
i
r
e
c
t
 
r
e
f
l
e
c
t
i
o
n
 
o
f
 
t
h
e
 
f
u
n
c
t
i
o
n
 
s
i
g
n
a
t
u
r
e
s
 
a
n
d
 
u
s
a
g
e
 
p
a
t
t
e
r
n
s
 
a
s
 
d
e
s
c
r
i
b
e
d
:




-
 
*
*
G
e
n
e
r
a
t
i
n
g
 
a
 
r
a
n
d
o
m
 
k
e
y
 
p
a
i
r
:
*
*


 
 
`
`
`
c
p
p


 
 
a
u
t
o
 
[
p
u
b
,
 
s
e
c
]
 
=
 
r
a
n
d
o
m
K
e
y
P
a
i
r
(
K
e
y
T
y
p
e
:
:
e
d
2
5
5
1
9
)
;


 
 
`
`
`




-
 
*
*
S
i
g
n
i
n
g
 
a
 
m
e
s
s
a
g
e
:
*
*


 
 
`
`
`
c
p
p


 
 
B
u
f
f
e
r
 
s
i
g
 
=
 
s
i
g
n
(
p
u
b
,
 
s
e
c
,
 
m
e
s
s
a
g
e
S
l
i
c
e
)
;


 
 
`
`
`




-
 
*
*
E
n
c
o
d
i
n
g
 
a
 
k
e
y
 
t
o
 
B
a
s
e
5
8
:
*
*


 
 
`
`
`
c
p
p


 
 
s
t
d
:
:
s
t
r
i
n
g
 
e
n
c
o
d
e
d
 
=
 
t
o
B
a
s
e
5
8
(
T
o
k
e
n
T
y
p
e
:
:
N
o
d
e
P
u
b
l
i
c
,
 
p
u
b
)
;


 
 
`
`
`




-
 
*
*
P
a
r
s
i
n
g
 
a
 
B
a
s
e
5
8
-
e
n
c
o
d
e
d
 
k
e
y
:
*
*


 
 
`
`
`
c
p
p


 
 
a
u
t
o
 
o
p
t
P
u
b
 
=
 
p
a
r
s
e
B
a
s
e
5
8
(
T
o
k
e
n
T
y
p
e
:
:
N
o
d
e
P
u
b
l
i
c
,
 
e
n
c
o
d
e
d
)
;


 
 
i
f
 
(
!
o
p
t
P
u
b
)
 
{
 
/
*
 
h
a
n
d
l
e
 
e
r
r
o
r
 
*
/
 
}


 
 
`
`
`




-
 
*
*
S
e
c
u
r
e
l
y
 
e
r
a
s
i
n
g
 
s
e
n
s
i
t
i
v
e
 
d
a
t
a
:
*
*


 
 
`
`
`
c
p
p


 
 
s
e
c
u
r
e
_
e
r
a
s
e
(
b
u
f
f
e
r
,
 
s
i
z
e
)
;


 
 
`
`
`




-
-
-




#
#
 
S
e
c
u
r
i
t
y
 
W
a
r
n
i
n
g
s
 
a
n
d
 
B
e
s
t
 
P
r
a
c
t
i
c
e
s




-
 
A
l
l
 
s
e
n
s
i
t
i
v
e
 
d
a
t
a
 
(
p
r
i
v
a
t
e
 
k
e
y
s
,
 
s
e
e
d
s
,
 
t
e
m
p
o
r
a
r
y
 
b
u
f
f
e
r
s
)
 
i
s
 
s
e
c
u
r
e
l
y
 
e
r
a
s
e
d
 
f
r
o
m
 
m
e
m
o
r
y
 
a
f
t
e
r
 
u
s
e
.


-
 
O
n
l
y
 
u
s
e
 
c
r
y
p
t
o
g
r
a
p
h
i
c
a
l
l
y
 
s
e
c
u
r
e
 
r
a
n
d
o
m
 
n
u
m
b
e
r
 
g
e
n
e
r
a
t
i
o
n
 
f
o
r
 
k
e
y
 
m
a
t
e
r
i
a
l
.


-
 
D
o
 
n
o
t
 
r
e
u
s
e
 
k
e
y
s
 
o
r
 
s
e
e
d
s
 
a
c
r
o
s
s
 
d
i
f
f
e
r
e
n
t
 
c
o
n
t
e
x
t
s
.


-
 
A
l
w
a
y
s
 
v
e
r
i
f
y
 
t
h
e
 
r
e
s
u
l
t
 
o
f
 
c
r
y
p
t
o
g
r
a
p
h
i
c
 
o
p
e
r
a
t
i
o
n
s
 
a
n
d
 
h
a
n
d
l
e
 
e
x
c
e
p
t
i
o
n
s
 
o
r
 
f
a
i
l
u
r
e
s
.


-
 
N
e
v
e
r
 
t
r
a
n
s
m
i
t
 
p
r
i
v
a
t
e
 
k
e
y
s
 
o
r
 
s
e
e
d
s
 
o
v
e
r
 
t
h
e
 
n
e
t
w
o
r
k
.


-
 
T
h
e
 
o
v
e
r
l
a
y
 
h
a
n
d
s
h
a
k
e
 
m
e
c
h
a
n
i
s
m
 
e
n
s
u
r
e
s
 
t
h
a
t
 
S
S
L
/
T
L
S
 
s
e
s
s
i
o
n
s
 
a
r
e
 
b
o
u
n
d
 
t
o
 
n
o
d
e
 
i
d
e
n
t
i
t
i
e
s
,
 
p
r
e
v
e
n
t
i
n
g
 
M
I
T
M
 
a
t
t
a
c
k
s
.


-
 
I
f
 
s
i
g
n
a
t
u
r
e
 
v
e
r
i
f
i
c
a
t
i
o
n
 
f
a
i
l
s
 
d
u
r
i
n
g
 
h
a
n
d
s
h
a
k
e
,
 
t
h
e
 
c
o
n
n
e
c
t
i
o
n
 
m
u
s
t
 
b
e
 
d
r
o
p
p
e
d
 
i
m
m
e
d
i
a
t
e
l
y
.




-
-
-




#
#
 
S
o
u
r
c
e
 
C
o
d
e
 
R
e
f
e
r
e
n
c
e
s




-
 
[
S
e
c
r
e
t
K
e
y
 
c
l
a
s
s
 
a
n
d
 
k
e
y
 
g
e
n
e
r
a
t
i
o
n
]
(
s
r
c
/
l
i
b
x
r
p
l
/
p
r
o
t
o
c
o
l
/
S
e
c
r
e
t
K
e
y
.
c
p
p
.
t
x
t
)


-
 
[
P
u
b
l
i
c
K
e
y
 
c
l
a
s
s
 
a
n
d
 
e
n
c
o
d
i
n
g
]
(
s
r
c
/
l
i
b
x
r
p
l
/
p
r
o
t
o
c
o
l
/
P
u
b
l
i
c
K
e
y
.
c
p
p
.
t
x
t
)


-
 
[
B
a
s
e
5
8
 
e
n
c
o
d
i
n
g
/
d
e
c
o
d
i
n
g
]
(
s
r
c
/
l
i
b
x
r
p
l
/
p
r
o
t
o
c
o
l
/
t
o
k
e
n
s
.
c
p
p
.
t
x
t
)


-
 
[
R
F
C
1
7
5
1
 
m
n
e
m
o
n
i
c
 
e
n
c
o
d
i
n
g
]
(
s
r
c
/
l
i
b
x
r
p
l
/
c
r
y
p
t
o
/
R
F
C
1
7
5
1
.
c
p
p
.
t
x
t
)


-
 
[
c
s
p
r
n
g
_
e
n
g
i
n
e
 
a
n
d
 
r
a
n
d
o
m
 
n
u
m
b
e
r
 
g
e
n
e
r
a
t
i
o
n
]
(
s
r
c
/
l
i
b
x
r
p
l
/
c
r
y
p
t
o
/
c
s
p
r
n
g
.
c
p
p
.
t
x
t
)


-
 
[
H
a
s
h
 
f
u
n
c
t
i
o
n
s
 
a
n
d
 
s
h
a
5
1
2
H
a
l
f
]
(
s
r
c
/
l
i
b
x
r
p
l
/
p
r
o
t
o
c
o
l
/
d
i
g
e
s
t
.
c
p
p
.
t
x
t
,
 
i
n
c
l
u
d
e
/
x
r
p
l
/
p
r
o
t
o
c
o
l
/
d
i
g
e
s
t
.
h
.
t
x
t
)


-
 
[
D
i
g
i
t
a
l
 
s
i
g
n
a
t
u
r
e
 
f
u
n
c
t
i
o
n
s
]
(
s
r
c
/
l
i
b
x
r
p
l
/
p
r
o
t
o
c
o
l
/
S
e
c
r
e
t
K
e
y
.
c
p
p
.
t
x
t
)


-
 
[
S
e
c
u
r
e
 
m
e
m
o
r
y
 
e
r
a
s
u
r
e
]
(
s
r
c
/
l
i
b
x
r
p
l
/
c
r
y
p
t
o
/
s
e
c
u
r
e
_
e
r
a
s
e
.
c
p
p
.
t
x
t
)


-
 
[
S
S
L
 
c
o
n
t
e
x
t
 
c
r
e
a
t
i
o
n
]
(
s
r
c
/
l
i
b
x
r
p
l
/
b
a
s
i
c
s
/
m
a
k
e
_
S
S
L
C
o
n
t
e
x
t
.
c
p
p
.
t
x
t
)


-
 
[
O
v
e
r
l
a
y
 
h
a
n
d
s
h
a
k
e
 
a
n
d
 
M
I
T
M
 
p
r
o
t
e
c
t
i
o
n
]
(
s
r
c
/
x
r
p
l
d
/
o
v
e
r
l
a
y
/
d
e
t
a
i
l
/
H
a
n
d
s
h
a
k
e
.
c
p
p
.
t
x
t
,
 
s
r
c
/
x
r
p
l
d
/
o
v
e
r
l
a
y
/
R
E
A
D
M
E
.
m
d
)




-
-
-




#
#
 
C
o
n
c
l
u
s
i
o
n




T
h
e
 
X
R
P
L
 
c
r
y
p
t
o
g
r
a
p
h
y
 
s
u
b
s
y
s
t
e
m
 
i
s
 
a
 
t
i
g
h
t
l
y
 
i
n
t
e
g
r
a
t
e
d
 
s
e
t
 
o
f
 
c
o
m
p
o
n
e
n
t
s
 
f
o
r
 
s
e
c
u
r
e
 
k
e
y
 
m
a
n
a
g
e
m
e
n
t
,
 
d
i
g
i
t
a
l
 
s
i
g
n
a
t
u
r
e
s
,
 
h
a
s
h
i
n
g
,
 
r
a
n
d
o
m
 
n
u
m
b
e
r
 
g
e
n
e
r
a
t
i
o
n
,
 
a
n
d
 
s
e
c
u
r
e
 
c
o
m
m
u
n
i
c
a
t
i
o
n
s
.
 
A
l
l
 
c
r
y
p
t
o
g
r
a
p
h
i
c
 
o
p
e
r
a
t
i
o
n
s
 
a
r
e
 
i
m
p
l
e
m
e
n
t
e
d
 
u
s
i
n
g
 
i
n
d
u
s
t
r
y
-
s
t
a
n
d
a
r
d
 
a
l
g
o
r
i
t
h
m
s
 
a
n
d
 
l
i
b
r
a
r
i
e
s
,
 
w
i
t
h
 
c
a
r
e
f
u
l
 
a
t
t
e
n
t
i
o
n
 
t
o
 
s
e
c
u
r
e
 
m
e
m
o
r
y
 
h
a
n
d
l
i
n
g
 
a
n
d
 
p
r
o
t
o
c
o
l
-
l
e
v
e
l
 
s
e
c
u
r
i
t
y
 
(
i
n
c
l
u
d
i
n
g
 
p
r
o
t
e
c
t
i
o
n
 
a
g
a
i
n
s
t
 
M
I
T
M
 
a
t
t
a
c
k
s
 
d
u
r
i
n
g
 
p
e
e
r
 
h
a
n
d
s
h
a
k
e
s
)
.
 
E
v
e
r
y
 
a
s
p
e
c
t
 
i
s
 
d
i
r
e
c
t
l
y
 
s
u
p
p
o
r
t
e
d
 
b
y
 
t
h
e
 
p
r
o
v
i
d
e
d
 
s
o
u
r
c
e
 
c
o
d
e
 
a
n
d
 
d
o
c
u
m
e
n
t
a
t
i
o
n
.




-
-
-




*
*
I
f
 
a
n
y
 
i
n
f
o
r
m
a
t
i
o
n
 
i
s
 
m
i
s
s
i
n
g
 
o
r
 
u
n
c
l
e
a
r
,
 
i
t
 
i
s
 
b
e
c
a
u
s
e
 
i
t
 
i
s
 
n
o
t
 
p
r
e
s
e
n
t
 
i
n
 
t
h
e
 
p
r
o
v
i
d
e
d
 
d
o
c
u
m
e
n
t
a
t
i
o
n
 
o
r
 
c
o
d
e
 
e
x
c
e
r
p
t
s
.
*
*


`
`
`