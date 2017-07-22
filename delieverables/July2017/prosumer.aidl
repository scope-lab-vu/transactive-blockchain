interface prosumer extends consumer{
	offerProduction(long amount, long time, byte[] signature);
}