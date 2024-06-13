from tasks import bulk_update
from apscheduler.schedulers.blocking import BlockingScheduler



# Crie uma instância do BlockingScheduler
scheduler = BlockingScheduler()

# Adicione a tarefa ao scheduler com um intervalo de 10 segundos
scheduler.add_job(bulk_update, 'interval', seconds=10)

try:
    # Inicie o scheduler
    print("Iniciando o scheduler...")
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    # Pare o scheduler em caso de interrupção (CTRL+C)
    print("Scheduler interrompido.")
    scheduler.shutdown()