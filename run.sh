./tigerbeetle format --cluster=0 --replica=0 --replica-count=1 tb_data.tigerbeetle
./tigerbeetle start \
	--addresses=0.0.0.0:3000 \
       	--development ./tb_data.tigerbeetle
