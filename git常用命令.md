## git常用命令

​	初始化仓库 :   git init 

​	创建并切换到分支:   git checkout -b dev

​	从GitHub仓库克隆文件:  git clone 加上一个链接

​	链接方式有两种:一种是Clone with HTTPS  另一张是Clone with SSH 	

​	前面的传输方式不安全  后面的需要配置ssh私钥和公钥 加密传输	

    1. https://github.com/Fulaiy/meiduo_mall.git

    2. git@github.com:Fulaiy/meiduo_mall.git

       

​	cd 克隆下来的文件夹中  比如  cd  meiduo_mall

​	写完代码后 提交

  		1.  git add . 或者文件名
  		2.  git commit -m  '备注信息 随便自己写'
  		3.  git push  origin  dev:dev   

​         别人修改过代码提交后 可以使用  git pull   自己这边就会把修改的代码档下来

​	查看状态   git status

​	

​	生成SSH的命令 :   ssh  -keygen  -t   rsa  



​	生成应用的私钥和公钥:

​		openssl

​		genrsa -out app_private_key.pem 2048  # 私钥RSA2

​		 rsa -in app_private_key.pem -pubout -out app_public_key.pem # 导出公钥

​	查看公钥 :   cat app_publict_key.pem







