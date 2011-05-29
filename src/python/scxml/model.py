from event import Event
from collections import deque	#this is a non-synchronized queue

class SCXMLModel():
	def __init__(self,rootState=None):
		self.root = rootState

	def __str__(self):
		allNodes = [self.root]
		allNodes.extend(self.root.getDescendants())
		allNodeStrings = map(lambda n : str(n),allNodes)
		return "\n".join(allNodeStrings) 

		

class State():
	BASIC = 0
	COMPOSITE = 1
	PARALLEL = 2
	#AND = 3
	HISTORY = 4
	INITIAL = 5
	FINAL = 6

	def __init__(self,name="",kind=BASIC,documentOrder=0):
		self.name = name
		self.kind = kind
		self.documentOrder = documentOrder

		self.enterActions = []
		self.exitActions = []
		self.transitions = []
		self.parent = None
		self.initial = None
		self.children = []

	def __str__(self):
		return self.name

	def __repr__(self):
		return "<" + str(self) + ">"

	def getDepth(self):
		count = 0
		state = self.parent
		while state:
			count = count + 1
			state = state.parent

		return count

	def getAncestors(self,root = None):
		ancestors = []

		state = self.parent
		while state is not root:
			ancestors.append(state)
			state = state.parent

		return ancestors

	def getAncestorsOrSelf(self,root=None):
		return [self] + self.getAncestors()

	def getDescendants(self):
		descendants = [] 
		queue = deque(self.children)

		while queue:
			state = queue.popleft()
			descendants.append(state)

			for child in state.children:
				queue.append(child)

		return descendants

	def getDescendantsOrSelf(self):
		return [self] + self.getDescendants()

	def isOrthogonalTo(self,s):
		#Two control states are orthogonal if they are not ancestrally
		#related, and their smallest, mutual parent is a Concurrent-state.
		return not self.isAncestrallyRelatedTo(s) and self.getLCA(s).kind is State.PARALLEL

	def isAncestrallyRelatedTo(self,s):
		#Two control states are ancestrally related if one is child/grandchild of another.
		return self in s.getAncestorsOrSelf() or s in self.getAncestorsOrSelf()

	def getLCA(self,s):
		commonAncestors = filter(lambda a : s in a.getDescendants(),self.getAncestors())
		lca = None
		if commonAncestors:
			lca = commonAncestors[0]

		return lca

class Transition():
	def __init__(self,event=None,documentOrder=0,cond=lambda : True):
		self.event = event 
		self.documentOrder = documentOrder
		self.cond = cond

		self.source = None 
		self.targets = None
		self.actions = []

	def __str__(self):
		return self.source.name + " -> " + repr([target.name for target in self.targets])

	def __repr__(self):
		return "<" + str(self) + ">"

	def getLCA(self):
		return self.source.getLCA(self.targets[0])

class Action():
	def __call__(self):
		pass

class SendAction(Action):
	def __init__(self,eventName="",timeout=0):
		self.eventName = eventName
		self.timeout = timeout

	def __call__(self,datamodel,eventList):
		eventList.add(Event(self.eventName))

class AssignAction(Action):
	def __init__(self,location="",expr=""):
		self.location = location
		self.expr = expr

	def __call__(self,datamodel,eventList):				#TODO: replace datamodel with scripting context
		#Memory Protocols: Small-step
		datamodel[self.location] = eval(self.expr)	#TODO: eval js code using spidermonkey bindings

class ScriptAction(Action):
	def __init__(self,code=""):
		self.code = code

	def __call__(self,datamodel,eventList):				#TODO: replace datamodel with scripting context
		eval(self.code)					#TODO: eval js using spidermonkey bindings

