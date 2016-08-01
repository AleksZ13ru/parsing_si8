#include <stdio.h>
#include <memory.h>
#include <assert.h>

/* максимальная длина пакета согласно протоколу ОВЕН */
#define maxFrameSize 21

/* максимальная длина ASCII-пакета включая маркеры и символ '\0'  */
#define maxAsciiFrameSize 45


/* расчет контрольной суммы */
unsigned short owenCRC16(unsigned char* packet, size_t length)
{
	size_t i, j;
	unsigned short crc;

	assert(packet);

	crc = 0;
	for (i = 0; i < length; ++i)
	{
		unsigned char b = packet[i];
		for (j = 0; j < 8; ++j, b <<= 1)
		{
			if ((b ^ (crc >> 8)) & 0x80)
			{
				crc <<= 1;
				crc ^= 0x8F57;
			}
			else
				crc <<= 1;
		}
	}
	return crc;
}

size_t frameAsciiRS(char* frameAsciiRecv, size_t frameAsciiReciveSize)
{
		frameAsciiReciveSize = sizeof(frameAsciiRecv)/sizeof(*frameAsciiRecv) - 1;
		return frameAsciiReciveSize;	
}

size_t framef(char* frameAsciiRecv, size_t frameAsciiReciveSize)
{
		frameAsciiReciveSize = sizeof(frameAsciiRecv);
		return frameAsciiReciveSize;
}

size_t frames(char* frameAsciiRecv, size_t frameAsciiReciveSize)
{
		frameAsciiReciveSize = sizeof(*frameAsciiRecv);
		return frameAsciiReciveSize;
}


size_t packFrame(unsigned short address, unsigned short addrLen, int request, unsigned int hash, size_t dataSize, unsigned char* data, unsigned short crc, int crc_ok, unsigned char* frame, size_t frameSize)
{
	unsigned short crc_c;

	assert(frameSize >= 6);

	if (addrLen == 8)
	{
		frame[0] = address & 0xff;
		frame[1] = 0;
	}
	else
	{
		frame[0] = (address >> 3)  & 0xff;
		frame[1] = (address & 0x07) << 5;
	}

	if (request)
		frame[1] |= 0x10;

	assert(dataSize <= 15);
	frame[1] |= dataSize;

	frame[2] = (hash >> 8) & 0xff;
	frame[3] = hash & 0xff;

	if (dataSize)
	{
		memcpy(frame+4, data, dataSize);
	}
	crc_c = owenCRC16(frame, 4 + dataSize);
	crc = crc_c;
	crc_ok = 1;

	frame[4 + dataSize] = (crc_c >> 8) & 0xff;
	frame[5 + dataSize] = crc_c & 0xff;

	return 6 + dataSize;
}

void unpackFrame(unsigned char* frame, size_t frameSize, unsigned short address, unsigned short addrLen, int request, unsigned int hash, size_t dataSize, unsigned char* data, unsigned short crc, int crc_ok)
{
	size_t dataSize_v;

	/* ВНИМАНИЕ: невозможно отличить 11-битые адреса кратные 8 от 8-битных */
	if (frame[1] & 0xe0)
	{
		address = (frame[0] << 3) | (frame[1] >> 5);
		addrLen = 11;
	}
	else
	{
		address = frame[0];
		addrLen = 8;
	}

	request = (frame[1] & 0x10) != 0;
	hash = (frame[2] << 8) | frame[3];
	dataSize_v = frame[1] & 0x0F;

	if (dataSize_v)
	{
		dataSize = dataSize_v;
		memcpy(data, frame + 4, dataSize_v);
	}
	else
	{
		dataSize = 0;
	}
	crc = (frame[frameSize-2] << 8) | frame[frameSize-1];
	crc_ok = crc == owenCRC16(frame, frameSize-2);
}

void packFrameToAscii(unsigned char* frame, size_t frameSize, char* frameAscii, size_t frameAsciiSize)
{
	size_t i, j;

	assert(frame && frameAscii);
	assert(frameAsciiSize >= frameSize*2+2+1);

	frameAscii[0] = '#';
	for (i = 0, j = 1; i < frameSize; ++i, j += 2)
	{
		frameAscii[j] = 'G' + ((frame[i] >> 4) & 0x0f);
		frameAscii[j + 1] = 'G' + (frame[i] & 0x0f);
	}
	frameAscii[frameSize*2+1] = '\xD';
	frameAscii[frameSize*2+2] = '\0';
}

void unpackAsciiFrame(char* frameAscii, size_t frameAsciiSize, unsigned char* frame, size_t frameSize)
{
	size_t i, j;

	assert(frameAscii && frame);
	assert(frameAscii[0] == '#');
	assert(frameSize >= (frameAsciiSize - 2)/2);

	for (i = 1, j = 0; i < frameAsciiSize-2;  i += 2, ++j)
	{
		assert('G' <= frameAscii[i]&&frameAscii[i] <= 'V');
		assert('G' <= frameAscii[i+1]&&frameAscii[i+1] <= 'V');

		frame[j] = (frameAscii[i] - 'G') << 4 | (frameAscii[i+1] - 'G');
	}
}


/* преобразование локального идентификатора в двоичный вид 

		name - локальный идентификатор
		length - длина идентификатора

		id - идентификатор в двоичном виде
*/
void name2id(char* name, size_t length, unsigned char id[4])
{
	size_t i, j;

	assert(name);
	assert(length);

	for (i = 0, j = 0; i < length && j <= 4; ++i)
	{
		unsigned char b;
		char c = name[i];

		if ('0' <= c && c <= '9')
		{
			b = c - '0';
		}
		else if ('a' <= c && c <= 'z')
		{
			b = 10 + c - 'a';
		}
		else if ('A' <= c && c <= 'Z')
		{
			b = 10 + c - 'A';
		}
		else if ('-' == c)
		{
			b = 10 + 26 + 0;
		}
		else if ('_' == c)
		{
			b = 10 + 26 + 1;
		}
		else if ('/' == c)
		{
			b = 10 + 26 + 2;
		}
		else if ('.' == c)
		{
			assert(i > 0); /* модификатор не может быть первым символом */
			assert(name[i-1] != '.'); /* не может быть двух модификаторов подряд */

			++id[j - 1];

			continue;
		}
		else if (' ' == c)
		{
			break; /* пробел может находиться только в конце имени */
		}
		else
			assert(0); /* недопустимый символ */

		id[j++] = b*2;
	}

	if (j == 4)
	{
		/* заполнены все байты идентификатора */
		assert(i == length); /* обработаны все символы имени */
	}
	else
	{
		/* встречен первый пробел или обработаны все символы имени */
		for (; i < length; ++i)
		{
			assert(name[i] == ' '); /* после пробела могут находиться только пробелы */
			assert(j < 4);

			id[j++] = 78;
		}

		/* дополняем пробелами до четырех символов */
		for (; j < 4; ++j)
			id[j] = 78;
	}
}

/* свертка локального идентификатора */
unsigned short id2hash(unsigned char id[4])
{
	size_t i, j;
	unsigned short hash;

	hash = 0;
	for (i = 0; i < 4; ++i)
	{
		unsigned char b = id[i];
		b <<= 1; /* используются только младшие 7 бит */
		for (j = 0; j < 7; ++j, b <<= 1)
		{
			if ((b ^ (hash >> 8)) & 0x80)
			{
				hash <<= 1;
				hash ^= 0x8F57;
			}
			else
				hash <<= 1;
		}
	}
	return hash;
}








int main(int argc, char* argv[])
{
	unsigned char frame[maxFrameSize];
	char frameAscii[maxAsciiFrameSize];
	size_t frameSize;

	return 0;
}
