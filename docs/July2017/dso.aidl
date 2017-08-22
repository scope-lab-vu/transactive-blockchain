interface DSO{
	boolean deploySmartContract(byte[] contract, byte[] signature);
	boolean deactivateSmartContract(byte[] contract, byte[] signature);
	long setPriceConsumption(float unitPrice, long timestamp, byte[] signature);
	long setPriceProduction(float unitPrice, long timestamp, byte[] signature);
	boolean addBannedSmartmeter(long id, long timestamp, byte[] signature);
	boolean addAuthorizedSmartMeter(long id, long timestamp, byte[] signature);
	boolean allocateCurrency(long id, long amount, byte[] signature);
}