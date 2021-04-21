import math
import time
import sys
from enum import Enum

path_input = './inputs/input_fara_solutie.txt'
path_output = './outputs/output.txt'
maxim_timp_program = 10 # in secunde


# golim fisierul output inainte
with open(path_output, 'w'):
	pass


class TipEuristicaEnum(Enum):
	BANALA = 'BANALA'
	ADMISIBILA = 'ADMISIBILA'

class NodParcurgere:
	gr = None
	def __init__(self, info, parinte, cost = 0, h = 0):
		self.info = info
		self.parinte = parinte
		self.g = cost # costul de la nodul de pornire la nodul curent
		self.h = h # costul estimat de la nodul curent la nodul scop
		self.f = self.g + self.h

	def obtineDrum(self):
		l = [self]
		nod = self

		while nod.parinte is not None:
			l.insert(0, nod.parinte)
			nod = nod.parinte

		return l

	def afisDrum(self, afisCost = False, afisLung = False):
		f = open(path_output, 'a')
		l = self.obtineDrum()
		for nod in l:
			if nod.parinte is not None:
				if nod.parinte.info[3] == 1:
					mbarca1 = self.__class__.gr.malInitial
					mbarca2 = self.__class__.gr.malFinal
				else:
					mbarca1 = self.__class__.gr.malFinal
					mbarca2 = self.__class__.gr.malInitial

				f.write(f'>> Barca s-a deplasat de la malul {mbarca1} la malul {mbarca2} cu {abs(nod.info[0] - nod.parinte.info[0])} copii, {abs(nod.info[1] - nod.parinte.info[1])} misionari si {abs(nod.info[2] - nod.parinte.info[2])} canibali\n\n')
			f.write(f'{nod}\n\n')
		if afisCost:
			f.write(f'Cost: {self.g}\n')
		if afisLung:
			f.write(f'Nr noduri: {len(l)}\n')
		f.write('\n===================\n')
		return len(l)

	def contineInDrum(self, infoNodNou):
		nodDrum = self

		while nodDrum is not None:
			if infoNodNou == nodDrum.info:
				return True
			nodDrum = nodDrum.parinte

		return False

	def __repr__(self):
		return str(self.info)

	def __str__(self):
		# print(self.info)
		if self.info[3] == 1:
			barcaMalInitial = '<barca>'
			barcaMalFinal = '       '
		else:
			barcaMalInitial = '       '
			barcaMalFinal = '<barca>'

		return (f'Mal: {self.gr.malInitial} Copii: {self.info[0]}, Misionari: {self.info[1]}, Canibali: {self.info[2]} {barcaMalInitial}  ||| {barcaMalFinal} Mal: {self.gr.malFinal} Copii: {self.__class__.gr.N0 - self.info[0]}, Misionari: {self.__class__.gr.N1 - self.info[1]}, Canibali: {self.__class__.gr.N2 - self.info[2]}')



class Graph:
	def __init__(self, nume_fisier):
		f = open(nume_fisier, 'r')
		listaInfoFisier = f.read().split()

		self.__class__.N0 = int(listaInfoFisier[0]) # numar copii
		self.__class__.N1 = int(listaInfoFisier[1]) # numar misionari
		self.__class__.N2 = int(listaInfoFisier[2]) # numar canibali
		self.__class__.M = int(listaInfoFisier[3]) # numar locuri in barca

		self.__class__.malInitial = listaInfoFisier[4] # denumirea malului initial
		self.__class__.malFinal = listaInfoFisier[5] # denumirea malului final

		self.start = (self.__class__.N0, self.__class__.N1, self.__class__.N2, 1) # nodul de inceput (fiecare personaj si barca se afla pe malul initial)
		self.scopuri = [(0, 0, 0, 0)]

	def testeaza_scop(self, nodCurent):
		return nodCurent.info in self.scopuri;

	def genereazaSuccesori(self, nodCurent, tip_euristica = TipEuristicaEnum.BANALA):

		def test_conditie(numar_copii, numar_misionari, numar_canibali):
			if numar_copii < 0 or numar_misionari < 0 or numar_canibali < 0:
				return
			# numar_misionari + numar_copii / 2 >= numar_canibali
			return 2 * numar_misionari + numar_copii >= 2 * numar_canibali

		listaSuccesori = []

		barca = nodCurent.info[3]

		# ne intereseaza malul in care se afla barca (i.e. malul curent)
		# daca barca se afla pe malul initial
		if barca == 1:
			copiiMalCurent = nodCurent.info[0]
			misionariMalCurent = nodCurent.info[1]
			canibaliMalCurent = nodCurent.info[2]

			copiiMalOpus = Graph.N0 - nodCurent.info[0]
			misionariMalOpus = Graph.N1 - nodCurent.info[1]
			canibaliMalOpus = Graph.N2 - nodCurent.info[2]
		# daca barca se afla pe malul opus
		else:
			copiiMalOpus = nodCurent.info[0]
			misionariMalOpus = nodCurent.info[1]
			canibaliMalOpus = nodCurent.info[2]

			copiiMalCurent = Graph.N0 - nodCurent.info[0]
			misionariMalCurent = Graph.N1 - nodCurent.info[1]
			canibaliMalCurent = Graph.N2 - nodCurent.info[2]

		copiiVeniti = 0

		# trebuie sa avem cel putin un misionar in barca cu copii, deci copii nu pot ocupa toate locurile din barca
		maxCopiiBarca = min(Graph.M - 1, copiiMalCurent)
		for copiiBarca in range(maxCopiiBarca + 1):

			# daca avem copii in barca, atunci trebuie sa avem cel putin un misionar in ea, altfel putem avea oricati misionari
			if copiiBarca != 0:
				maxMisionariBarca = min(Graph.M, misionariMalCurent - 1)
			else:
				maxMisionariBarca = min(Graph.M, misionariMalCurent)

			for misionariBarca in range(maxMisionariBarca + 1):
				if copiiBarca != 0 and misionariBarca == 0:
					continue

				if misionariBarca == 0:
					maxCanibaliBarca = min(Graph.M, canibaliMalCurent)
					minCanibaliBarca = 1
				else:
					# 2 copii sunt echivalentul la 1 misionar
					maxCanibaliBarca = min(Graph.M, misionariBarca + math.ceil(copiiBarca / 2))
					minCanibaliBarca = 0

				for canibaliBarca in range(minCanibaliBarca, maxCanibaliBarca + 1):

					# iesim din pasul curent daca barca este goala
					if copiiBarca + misionariBarca + canibaliBarca == 0:
						continue

					# iesim din pasul curent daca umplem capacitatea barcii
					if copiiBarca + misionariBarca + canibaliBarca > Graph.M:
						continue

					# todo: completeaza cu celelalte conditii
					# - obs: nu uita ca un copil nu poate pleca imediat

					# if copiiBarca >= copiiVeniti - copiiMalOpus:
					# 	continue

					copiiMalCurentNou = copiiMalCurent - copiiBarca
					misionariMalCurentNou = misionariMalCurent - misionariBarca
					canibaliMalCurentNou = canibaliMalCurent - canibaliBarca

					copiiMalOpusNou = copiiMalOpus + copiiBarca
					misionariMalOpusNou = misionariMalOpus + misionariBarca
					canibaliMalOpusNou = canibaliMalOpus + canibaliBarca

					if not test_conditie(copiiMalCurentNou, misionariMalCurentNou, canibaliMalCurentNou):
						continue

					if not test_conditie(copiiMalOpusNou, misionariMalOpusNou, canibaliMalOpusNou):
						continue

					# ne intereseaza ca nodul creat sa contina starea malului initial (malul final il putem deduce din malul initial)
					if barca == 1:
						infoNodNou = (copiiMalCurentNou, misionariMalCurentNou, canibaliMalCurentNou, 0)
					else:
						infoNodNou = (copiiMalOpusNou, misionariMalOpusNou,  canibaliMalOpusNou, 1)
					print(infoNodNou)
					if not nodCurent.contineInDrum(infoNodNou):
						copiiVeniti = copiiBarca
						# costSuccesor = 1 + copiiBarca
						costSuccesor = 0
						listaSuccesori.append(NodParcurgere(infoNodNou, nodCurent, cost=nodCurent.g + costSuccesor, h=NodParcurgere.gr.calculeaza_h(infoNodNou, tip_euristica)))
		return listaSuccesori

	def calculeaza_h(self, infoNod, tip_euristica = TipEuristicaEnum.BANALA):
		if tip_euristica == TipEuristicaEnum.BANALA:
			if infoNod not in self.scopuri:
				return 1
			return 0
		else:
			return 2 * math.ceil((infoNod[0] / 2 + infoNod[1] + infoNod[2]) / (self.M - 1)) + (1 - infoNod[3]) - 1

	def __repr__(self):
		sir = ''

		for (k, v) in self.__dict__.items():
			sir += f'{k} = {v} '

		return sir


def bf(gr, nrSolutiiCautate = 1):
	c = [NodParcurgere(gr.start, None)]

	timp_total = 0
	while len(c) > 0:
		t1 = time.time()
		nodCurent = c.pop(0)

		if gr.testeaza_scop(nodCurent):
			print('Solutie:')
			nodCurent.afisDrum(afisCost=True, afisLung=True)
			input()

			# resetam timpul pentru fiecare solutie
			timp_total = 0
			t1 = time.time()
			nrSolutiiCautate -= 1

			if nrSolutiiCautate == 0:
				return
		listaSuccesori = gr.genereazaSuccesori(nodCurent)
		c.extend(listaSuccesori)
		t2 = time.time()

		timp_total += t2 - t1 * 1000

		if timp_total > maxim_timp_program:
			print('timp program depasit!')
			exit(0)


def ucs(gr, nrSolutiiCautate = 1):
	c = [NodParcurgere(gr.start, None, 0, 0)]

	timp_total = 0

	while len(c) > 0:
		t1 = time.time()
		nodCurent = c.pop(0)

		if gr.testeaza_scop(nodCurent):
			print('Solutie: ')
			nodCurent.afisDrum(afisCost = True, afisLung = True)
			input()

			# resetam timpul pentru fiecare solutie
			timp_total = 0
			t1 = time.time()

			nrSolutiiCautate -= 1

			if nrSolutiiCautate == 0:
				return

		listaSuccesori = gr.genereazaSuccesori(nodCurent)

		for succesor in listaSuccesori:
			i = 0
			gasit_loc = False

			for i in range(len(c)):
				if c[i].g > succesor.g:
					gasit_loc = True
					break

			if gasit_loc:
				c.insert(i, succesor)
			else:
				c.append(succesor)

		t2 = time.time()

		timp_total += t2 - t1

		if timp_total > maxim_timp_program:
			print('timp program depasit!')
			exit(0)

def a_star(gr, nrSolutiiCautate = 1, tip_euristica = TipEuristicaEnum.BANALA):
	#in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
	c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]
	timp_total = 0
	while len(c) > 0:
		t1 = time.time()
		nodCurent = c.pop(0)

		if gr.testeaza_scop(nodCurent):
			print('Solutie: ')
			nodCurent.afisDrum(afisCost = True, afisLung = True)
			input()

			# resetam timpul pentru fiecare solutie
			timp_total = 0
			t1 = time.time()

			nrSolutiiCautate -= 1
			if nrSolutiiCautate == 0:
				return

		listaSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)

		for succesor in listaSuccesori:
			i = 0
			gasit_loc = False
			for i in range(len(c)):
				if c[i].f >= succesor.f:
					gasit_loc = True
					break

			if gasit_loc:
				c.insert(i,succesor)
			else:
				c.append(succesor)

		t2 = time.time()

		timp_total += t2 - t1

		if timp_total > maxim_timp_program:
			print('timp program depasit!')
			exit(0)

def ida_star(gr, nrSolutiiCautate = 1):
	nodStart = NodParcurgere(gr.start, None, 0, 0)
	limita = nodStart.f

	while True:
		nrSolutiiCautate, rezultat = construieste_drum(gr, nodStart, limita, nrSolutiiCautate)

		if rezultat == 'gata':
			break

		if rezultat == float('inf'):
			print('Nu exista solutii')
			break

		limita = rezultat
		input()

def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate):
	timp_total = 0
	if nodCurent.f > limita:
		return nrSolutiiCautate, nodCurent.f

	if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
		print('Solutie: ')
		nodCurent.afisDrum()
		input()

		nrSolutiiCautate -= 1

		if nrSolutiiCautate == 0:
			return 0, 'gata'

	listaSuccesori = gr.genereazaSuccesori(nodCurent)
	minim = float('inf')

	for succesor in listaSuccesori:
		nrSolutiiCautate, rezultat = construieste_drum(gr, succesor, limita, nrSolutiiCautate)

		if rezultat == 'gata':
			return 0, 'gata'

		if rezultat < minim:
			minim = rezultat

	return nrSolutiiCautate, minim


# initializare problema
gr = Graph(path_input)
NodParcurgere.gr = gr

# bf(gr, 2)
a_star(gr, 5, tip_euristica = TipEuristicaEnum.ADMISIBILA)
# ucs(gr, 5)
# ida_star(gr, 5)


