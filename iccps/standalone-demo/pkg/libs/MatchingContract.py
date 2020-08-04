from libs.Contract import Contract
from libs.Enums import *


class MatchingContract(Contract):

	def setup(self, from_account, getReceipt, _Cint, _Cext, _nextInterval):
		return self.call_func(from_account, getReceipt, 0, "setup", 
			"uint64", _Cint,
			"uint64", _Cext,
			"uint64", _nextInterval
		)

	def registerProsumer(self, from_account, getReceipt, prosumer, feeder):
		return self.call_func(from_account, getReceipt, 0, "registerProsumer", 
			"uint64", prosumer,
			"uint64", feeder
		)

	def postBuyingOffer(self, from_account, getReceipt, prosumer, startTime, endTime, energy, value):
		return self.call_func(from_account, getReceipt, 0, "postBuyingOffer", 
			"uint64", prosumer,
			"uint64", startTime,
			"uint64", endTime,
			"uint64", energy,
			"uint64", value
		)

	def postSellingOffer(self, from_account, getReceipt, prosumer, startTime, endTime, energy, value):
		return self.call_func(from_account, getReceipt, 0, "postSellingOffer", 
			"uint64", prosumer,
			"uint64", startTime,
			"uint64", endTime,
			"uint64", energy,
			"uint64", value
		)

	def startSolve(self, from_account, getReceipt, interval):
		return self.call_func(from_account, getReceipt, 0, "startSolve", 
			"uint64", interval
		)

	def submitClearingPrice(self, from_account, getReceipt, interval, price):
		return self.call_func(from_account, getReceipt, 0, "submitClearingPrice", 
			"uint64", interval,
			"uint64", price
		)

	def __init__(self, client, address):
		super().__init__(client, address, {'StartOffering': [('interval', 'uint64')], 'ProsumerRegistered': [('prosumer', 'uint64'), ('feeder', 'uint64')], 'BuyingOfferPosted': [('ID', 'uint64'), ('prosumer', 'uint64'), ('startTime', 'uint64'), ('endTime', 'uint64'), ('energy', 'uint64'), ('value', 'uint64')], 'SellingOfferPosted': [('ID', 'uint64'), ('prosumer', 'uint64'), ('startTime', 'uint64'), ('endTime', 'uint64'), ('energy', 'uint64'), ('value', 'uint64')], 'Solve': [('interval', 'uint64')], 'ClearingPrice': [('interval', 'uint64'), ('price', 'uint64')]})
