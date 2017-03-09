#ifndef PF_H_INCLUDED
#define PF_H_INCLUDED
#include <stdio.h>
#include <string.h>
#include <sys/shm.h>
#include <stdlib.h>

struct operate_info
{
    int thread_id;
    int pthread_op_id;
    char share_val[20];
};

void instr(int pthread_op_id, char share_val[20])
{
    // get share mem id
    char *shmid = getenv("PTHREAD_SHMID");
    int id;
    sscanf(shmid, "%d", &id);

    // convert to struct array
    struct operate_info *info_queue = (struct operate_info*)shmat(id, NULL, 0);

    // get array index
    char *shm_index = getenv("SHM_INDEX");
    int index;
    sscanf(shm_index, "%d", &index);

    // construct a info struct
    struct operate_info info;
    info.thread_id = pthread_self();
    info.pthread_op_id = pthread_op_id;
    strcpy(info.share_val, share_val);

    // write the info into share mem
    info_queue[index] = info;

    // update array index
    sprintf(shm_index, "%d", index+1);
    setenv("SHM_INDEX", shm_index, 1);
}
#endif // PF_H_INCLUDED
