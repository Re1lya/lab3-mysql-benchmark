# 私有镜像
FROM swr.cn-north-4.myhuaweicloud.com/oomall-javaee/openjdk:21-alpine
# 官方镜像
#FROM openjdk:17-alpine
MAINTAINER mingqiu mingqiu@xmu.edu.cn
WORKDIR /app
ARG JAR_FILE
ADD ${JAR_FILE} /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
CMD []
