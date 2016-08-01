def BCD (data):
	signbit=data[0] & 0x80
	if signbit: 
		sign=-1
	else: 
		sign=1
	point=data[0] & 0x70 
	point=point >> 4
	val = data[0] & 0x0F
	for i in range(1,4):
		val=val*10
		temp1=data[i] & 0xF0
		temp2=temp1>>4
		val=val+temp2
		val=val*10
		val=val+(data[i] & 0x0F)
	value=sign*val*(10**(-point))
	return value

