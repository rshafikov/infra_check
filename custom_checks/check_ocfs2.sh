
OCFS2_IPS
IP=1
for ocfs2_ip in $OCFS2_IPS
do
    if [ ! "$ocfs2_ip" = "$IP" ]; then
        result=$(ssh $ocfs2_ip "if [ -e /etc/ocfs2/cluster.conf.done ]; then echo yes; fi")
        if [ ! "a$result" = "a" ] && [ $result = "yes" ]; then 
            echo "scp $ocfs2_ip:/etc/ocfs2/cluster.conf /etc/ocfs2"
            OCFS2_IP=$ocfs2_ip
        fi
        if [ -e /etc/ocfs2/cluster.conf ]; then
            break
        fi
    fi
done