configs=(qlearn_train qlearn_train1 qlearn_train2 qlearn_train3 qlearn_train4 qlearn_train5 qlearn_train6)

end=$((SECONDS+300))
while [ $SECONDS -lt $end ]; do
    rand=$[ $RANDOM % 7 ]
    java -jar /home/ubuntu/orbis/Launcher.jar -nogui-l -nogui-s -config ${configs[$rand]}
done
