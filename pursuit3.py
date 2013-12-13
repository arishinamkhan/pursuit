import sys
import random
import ast

TAU = 0.69	    #lexicon entry threshold
GAMMA = 0.01        #learning rate
LAMBDA = 0.001      #smoothing factor


def get_max_asc(meaning):
	"""Takes a meaning and returns its best label(with some word)"""
	idx = all_meanings.index(meaning)
	max_asc = max([v[idx] for v in asc.values()])
	return max_asc

def initialize(word, utt_meanings):
	"""Pairs unseen word with minimum best label meaning equalling to GAMMA"""
	best_labels = [(meaning, get_max_asc(meaning)) for meaning in utt_meanings]
	minval = min(best_labels, key = lambda x:x[1])
	idx = all_meanings.index(minval[0])
	asc[word][idx] = GAMMA
	
def reward(word, utt_meanings):
	"""Returns True if most probable meaning is confirmed, False otherwise"""
	max_asc = max(asc[word])
	max_sample_idx = random.choice([idx for idx, item in enumerate(asc[word]) if item==max_asc])
	most_prob_meaning = all_meanings[max_sample_idx]
	if most_prob_meaning in utt_meanings:
		return True, max_sample_idx
	return False, max_sample_idx
				
def prob(assoc, sum_assoc, n):
	"""Returns word-meaning association for deciding entry to lexicon"""
	prob = float(assoc+LAMBDA)/float(sum_assoc+n*LAMBDA)
	return prob

def build_lex():
	"""Builds and returns lexicon"""
	lex = []
	for w, v in asc.items():
		for idx, val in enumerate(v):
			if prob(val, sum(v), len(all_meanings))>TAU:
				lex.append((w,all_meanings[idx]))
	return lex

def pursuit(utt_words, utt_meanings):
	"""Implements Pursuit word learning algorithm"""
	for word in utt_words:
		#Initialize previously unseen word
		if sum(asc[word])==0:
			initialize(word, utt_meanings)
		#Adjust based on whether rewarded
		reward_flag, midx = reward(word, utt_meanings)
		val = asc[word][midx]
		if reward_flag:
			asc[word][midx] = val+GAMMA*(1-val)#<--reward most probable meaning
		else:
			asc[word][midx] = val*(1-GAMMA)#<--penalize most probable meaning
			#Reward visible meaning at random
			rand_meaning = random.choice(utt_meanings)
			rand_meaning_idx = all_meanings.index(rand_meaning) 
			asc[word][rand_meaning_idx] = asc[word][rand_meaning_idx]+GAMMA*(1-asc[word][rand_meaning_idx])		

def evaluate(lex):
	"""Evaluates current lexicon against gold standard, returns precision and recall"""
	correct = 0
	learnt = len(lex)-1
	goldlength = 34
	for item in lex:
		if item[1] == gold(item[0]): correct+=1
	precision = float(correct)/float(learnt)
	recall = float(correct)/float(goldlength)
	return precision, recall, lex						

def gold(word):
	"""Returns gold standard meaning for word"""
	gold = {"baby":"BABY", "bigbird":"BIRD", "bird":"DUCK",
	"moocows":"COW", "cows":"COW", "eyes":"EYES", "books":"BOOK",
	"duckie":"DUCK", "hand":"HAND", "kitty":"CAT", "kittycats":"CAT",
	"ring":"RING", "piggies":"PIG", "pig":"PIG", "lambie":"LAMB",
	"sheep":"LAMB", "birdie":"DUCK", "bear":"BEAR", "bigbirds":"BIRD",
	"moocow":"COW", "cow":"COW", "bunny":"BUNNY", "book":"BOOK",
	"duck":"DUCK", "hat":"HAT", "kittycat":"CAT", "lamb":"LAMB",
	"rings":"RING", "rattle":"RATTLE", "piggie":"PIG", "rabbit":"BUNNY",
	"bunnies":"BUNNY", "mirror":"MIRROR", "bottle":"BOTTLE"}
	try:
		return gold[word]
	except:
		return None

def prepare():
	"""Initializes data structures"""
	all_words = []
	inw = open("frank.all_words.txt")
	inm = open("frank.all_meanings.txt")
	for line in inw.readlines():
		all_words.append(line.strip("\n"))
	for line in inm.readlines():
		all_meanings.append(line.strip("\n"))
	#Initialize word-meaning associations dictionary
	for word in all_words:
		asc[word] = len(all_meanings)*[0]	
	#Initialize utterance data
	dataset = []
	inw = open("frank.uttered.txt")
	inm = open("frank.visible.txt")
	for line in inw.readlines():
		utt_words = ast.literal_eval(line.split(":")[1])
		meanings = inm.readline()
		utt_meanings = ast.literal_eval(meanings.split(":")[1]) 
		dataset.append((utt_words, utt_meanings))
	return dataset
	
if __name__ == "__main__":
	num = int(sys.argv[1])
	pav = 0
	rav = 0
	for i in range(num):
		asc = {}
		all_meanings = []
		dataset = prepare()
		for data in dataset:
			pursuit(data[0], data[1])
		p, r, lex = evaluate(build_lex())
		pav = pav + p
		rav = rav + r
		for item in lex:
			print "[lex "+str(i+1)+"] "+str(item[0])+": "+str(item[1])
		print "\n"
	print "precision: "+str(pav/num)
	print "recall   : "+str(rav/num)
	print "f        : "+str(2/((num/pav)+(num/rav)))

	
	
	
	
