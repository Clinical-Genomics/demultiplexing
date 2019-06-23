rm /home/proj/stage/flowcells/hiseqx/180119_ST-E00266_0265_AHHHVTCCXY/demuxstarted.txt
#rm -rf /home/proj/stage/demultiplexed-runs/180119_ST-E00266_0265_AHHHVTCCXY/tmp/
rm -rf /home/proj/stage/demultiplexed-runs/180119_ST-E00266_0265_AHHHVTCCXY/
#cp -rl /home/proj/stage/demultiplexed-runs/180119_ST-E00266_0265_AHHHVTCCXY.bak /home/proj/stage/demultiplexed-runs/180119_ST-E00266_0265_AHHHVTCCXY/
#rm -rf /home/proj/stage/demultiplexed-runs/180119_ST-E00266_0265_AHHHVTCCXY/l*/
#rm -rf /home/proj/stage/demultiplexed-runs/180119_ST-E00266_0265_AHHHVTCCXY/LOG/
bash ~/git/demultiplexing/scripts/hiseqx/xcheckfornewrun.bash /home/proj/stage/flowcells/hiseqx/ /home/proj/stage/demultiplexed-runs/
#less $(ls -1 -tr /home/proj/stage/demultiplexed-runs/180119_ST-E00266_0265_AHHHVTCCXY/LOG/Xdem-l1t11-HHHVTCCXY* | tail -2)
