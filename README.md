There are various types of memory 
using python to create a working memory which will take care of current memory
using sqlite to take care of episodal memory fact 
wont giving context will cost lot of tokens ?
we are not content stuffing (dumping all memory all at once)
we are emphasizing on selective retrieval (3-5 relevant memories for their specific prompt)

lets go through three patterns:
1)Pre Prompt Injection - the user ai query do u know about this msg and then sent 3 relative memory to the prompt

2)Confidence filtering - if a memory is in the ai bus but what if its too old then there comes the confidence score 

3)Tiered Injection- there are different type of memories like working mrmory,episodic memory,semantic memory if we inject all three at once that will lead to wastage of tokens



