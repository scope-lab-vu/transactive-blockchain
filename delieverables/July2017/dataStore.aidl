interface dataStore{
	UUID storeData(byte[] publicKey, byte[] data);
	byte[] getData(UUID uuid);
}