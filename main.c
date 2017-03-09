#include <stdio.h>
#include <sys/shm.h>
#include <unistd.h>
#include <pthread.h>

#include "pf.h" //instr

void thread1()
{
    int i;
    for(i = 0; i < 10; i ++)
    {
        printf("%d: step %d.\n", pthread_self(), i);
    }
}

void thread2()
{
    int i;
    for (i = 0; i < 10; i++)
    {
        printf("%d: step %d.\n", pthread_self(), i);
    }
}

int main()
{
    int shm_id = shmget(0xDEAD, 4096, 0666 | IPC_CREAT);
    char shmid_str[10];
    sprintf(shmid_str, "%d", shm_id);
    setenv("PTHREAD_SHMID", shmid_str, 1);

    struct operate_info* mem = (struct operate_info*)shmat(shm_id, NULL, 0);
    memset(mem, 0, 4096);

    pthread_spinlock_t lock;
    char spinlock_ptr[17];
    sprintf(spinlock_ptr, "%x", &lock);
    setenv("PTHREAD_SPINLOCK", spinlock_ptr, 0);

    char shm_index[10];
    sprintf(shm_index, "%d", 0);
    setenv("SHM_INDEX", shm_index, 1);

    pid_t pid = fork();
    if(pid == 0)
    {
        pthread_t id1, id2;
        int ret2 = pthread_create(&id2, NULL, thread2, NULL);
        instr(0x01, "create");  //instr
        int ret1 = pthread_create(&id1, NULL, thread1, NULL);
        instr(0x01, "create");  //instr

        pthread_join(id2, NULL);
        instr(0x02, "join");
        pthread_join(id1, NULL);
        instr(0x02, "join");

    }
    else
    {
        while(1)
        {
            if(mem[0].pthread_op_id == 1 && mem[1].pthread_op_id == 1 && mem[2].pthread_op_id == 2 && mem[3].pthread_op_id == 2)
            {
                printf("OK!\n");
                shmctl(shm_id, IPC_RMID, 0);
                break;
            }
            else
            {
            	sleep(1);
            }
        }
    }
}



