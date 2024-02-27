import numpy as np
import random

CRYPT = np.array([
	# annotated right to left
	[[0, 1, 0, 0], [0, 0, 0, 1], [1, 1, 0, 0], [0, 0, 1, 0]],       # right ear
	[[0, 0, 0, 1], [1, 0, 1, 0], [0, 0, 0, 0], [0, 1, 0, 0]],       # left ear
	[[1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 1], [1, 0, 0, 0]],       # with door
	[[0, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]        # "dots to dots"
	])

def stream_diagy():
	# order of pages is
	# A: WD, RE
	# B: LE, DD
	a_pages = [2, 0]
	b_pages = [3, 1]

	for N in range(4):
		for page in a_pages:
			for b in range(4):
				yield CRYPT[page][N][3-b]

	for N in range(4):
		for page in b_pages:
			for b in range(4):
				yield CRYPT[page][N][3-b]


pages = list(stream_diagy())
pages = np.array(pages).reshape((8, 8))

print("""Welcome to the Crypt!

Here are the faces arranged into one 8x8 matrix:
""")
print(pages)

def calc_parity_pages(mapp):
	P = np.zeros((6, ))
	pval = 0
	for N in range(6):
		parity_at_n = 0
		for idx in range(64):
			if idx & (2 ** N):
				y = idx // 8
				x = idx % 8
				parity = mapp[x][y]
				if parity:
					parity_at_n = 1 - parity_at_n

		P[5-N] = parity_at_n
		pval = (parity_at_n << N) + pval

	return (P, pval)

parity = calc_parity_pages(pages)

def calc_identity(mapp):
	sidebits = []
	bw = 0
	abw = 0
	for y in range(8):
		for x in range(8):
			if x == y:
				bw = (bw << 1) + mapp[x][y]
				mapp[x][y] = 8
			elif x == (7-y):
				abw += mapp[x][y] << y
				# abw = (abw << 1) + mapp[x][y]
				mapp[x][y] = 8
			else:
				sidebits.append(mapp[x][y])

	return (sidebits, bw, abw)

print("\n------- HEADER ---------")
(sidebits, bw, abw) = calc_identity(pages.copy())
print("""Identity: \t\t'{}' ({})
AntiIdentity: \t'{}' ({})
Parity: \t\t'{}' ({})""".format(chr(bw), bw, chr(abw), abw, chr(parity[1]), parity[1]))

# Read the rings
# Each ring will have a parity bit in the middle
# that would assume the middle bit is 1 to create parity with the outer ring.
print("\n-------- RINGS ---------")
ring_vals = [0,0,0,0]
for rot in range(4):

	# the rings
	if rot % 2 == 0:
		b = ((pages[2, 2] << 7) +
			 (pages[2, 1] << 6) +
			 (pages[2, 0] << 5) +
			 (pages[1, 0] << 4) +
			 (pages[0, 0] << 3) +
			 (pages[0, 1] << 2) +
			 (pages[0, 2] << 1) +
			 (pages[1, 2] << 0))
	else:
		b = ((pages[2, 2] << 7) +
			 (pages[1, 2] << 6) +
			 (pages[0, 2] << 5) +
			 (pages[0, 1] << 4) +
			 (pages[0, 0] << 3) +
			 (pages[1, 0] << 2) +
			 (pages[2, 0] << 1) +
			 (pages[2, 1] << 0))

	p = ((pages[2, 2]) ^
		 (pages[2, 1]) ^
		 (pages[2, 0]) ^
		 (pages[1, 0]) ^
		 (pages[0, 0]) ^
		 (pages[0, 1]) ^
		 (pages[0, 2]) ^
		 (pages[1, 2]))

	ring_vals[rot] = b

	parity = pages[1, 1]
	assert(p ^ parity)

	pages = np.rot90(pages)

print("""
	parity ok! (:

ascii rings:
 diagonal A: '{}' ({})
   			 '{}' ({})
 diagonal B: '{}' ({})
			 '{}' ({})

"Id" is a clear reference to the word identity, which also calls
to mind the position of these ascii characters.

The backtick '`' is called a "grave" which is a reference to the
crypt which contains it.

The 'currency symbol' is also called the 'scarab', making this a
clever reference to the Gold Bug cryptography story by Edgar Allen Poe.

Each ring of ascii encircles a parity bit:
P = b0 ^ b1 ^ b2 ... ^ b7 ^ 1*
		* the implied 1 at the end is important for ... later things

thanks for playing <3 - jw
""".format(chr(ring_vals[3]), ring_vals[3],
			chr(ring_vals[1]), ring_vals[1],
			chr(ring_vals[0]), ring_vals[0],
			chr(ring_vals[2]), ring_vals[2]))
