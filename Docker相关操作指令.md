## docker 的启动与停止

​	启动dockersudo service docker start

​	停止dockersudo service docker stop

​	重启dockersudo service docker restart

## docker镜像的操作

​	列出镜像: docker image ls

​	拉取镜像: docker image pull library/hello-world  也可以省略library

​	删除镜像: docker image rm 镜像名或镜像id

## docker容器操作

​	创建容器

```
docker run [option] 镜像名 [向启动容器中传入的命令]
```

常用可选参数说明：

- -i 表示以“交互模式”运行容器
- -t 表示容器启动后会进入其命令行。加入这两个参数后，容器创建就能登录进去。即 分配一个伪终端。
- --name 为创建的容器命名
- -v 表示目录映射关系(前者是宿主机目录，后者是映射到宿主机上的目录，即 宿主机目录:容器中目录)，可以使 用多个-v 做多个目录或文件映射。注意:最好做目录映射，在宿主机上做修改，然后 共享到容器上。
- -d 在run后面加上-d参数,则会创建一个守护式容器在后台运行(这样创建容器后不 会自动登录容器，如果只加-i -t 两个参数，创建后就会自动进去容器)。
- -p 表示端口映射，前者是宿主机端口，后者是容器内的映射端口。可以使用多个-p 做多个端口映射
- -e 为容器设置环境变量
- --network=host 表示将主机的网络环境映射到容器中，容器的网络与主机相同

#### 交互式容器

例如，创建一个交互式容器，并命名为myubuntu

```
docker run -it --name=myubuntu ubuntu /bin/bash
```

在容器中可以随意执行linux命令，就是一个ubuntu的环境，当执行exit命令退出时，该容器也随之停止。

#### 守护式容器

创建一个守护式容器:如果对于一个需要长期运行的容器来说，我们可以创建一个守护式容器。在容器内部exit退出时，容器也不会停止。

```
docker run -dit --name=myubuntu2 ubuntu
```

#### 进入已运行的容器

```
docker exec -it 容器名或容器id 进入后执行的第一个命令
```

如

```
docker exec -it myubuntu2 /bin/bash
```

#### 查看容器

```
# 列出本机正在运行的容器
docker container ls

# 列出本机所有容器，包括已经终止运行的
docker container ls --all
```

#### 停止与启动容器

```
# 停止一个已经在运行的容器
docker container stop 容器名或容器id

# 启动一个已经停止的容器
docker container start 容器名或容器id

# kill掉一个已经在运行的容器
docker container kill 容器名或容器id
```

#### 删除容器

```
docker container rm 容器名或容器id
```

## 将容器保存为镜像

我们可以通过如下命令将容器保存为镜像

```
docker commit 容器名 镜像名
```

## 镜像备份与迁移

我们可以通过save命令将镜像打包成文件，拷贝给别人使用

```
docker save -o 保存的文件名 镜像名
```

如

```
docker save -o ./ubuntu.tar ubuntu
```

在拿到镜像文件后，可以通过load方法，将镜像加载到本地



