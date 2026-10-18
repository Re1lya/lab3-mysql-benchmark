# Docker 升级评估

核对日期：2026 年 10 月 18 日。范围：实验三指导书、当前 4. SpringAOP 源码及部署脚本、四台服务器的只读检查。此次未升级、重启或重新部署服务器。

## 结论

本次实验验收前保留四台一致的 Docker 20.10.21。当前实验不依赖新版本特性，升级不能直接解决指导书中的路径、密码、内存或 JMeter 参数适配问题。长期维护值得升级，但建议在验收完成后，把受支持的 Ubuntu、Docker、containerd/runc 和构建工具作为一次独立迁移，在测试环境验证后实施。

## 指导书是否要求 stack config

没有。实验三 PDF 第 1 页要求四台 Ubuntu 18.04 并安装 Docker，没有固定 Docker 版本；第 3 页描述 Maven 构建、监控和 JMeter，没有 docker stack config。此前该命令来自整理材料时增加的只读配置校验，不是课程要求。实际部署脚本执行 docker stack deploy --resolve-image never -c 配置文件 lab。

docker stack config 用于展开变量、合并并输出配置，不负责部署。当前服务器 CLI 没有该子命令；上游 20.10.21 的命令注册也没有它，因此不把该报错视为应用或集群故障。参考：[当前命令文档](https://docs.docker.com/reference/cli/docker/stack/config/)、[20.10.21 命令源码](https://github.com/docker/cli/blob/v20.10.21/cli/command/stack/cmd.go)。

## 实际版本依赖

| 部分 | 发现 | 升级影响 |
| --- | --- | --- |
| 操作系统与运行时 | 四台 Ubuntu 18.04.6，内核 4.15.0-213，Docker 20.10.21，API 1.41 | 不能只按最新版安装页在旧系统直接替换 |
| 包来源 | Ubuntu docker.io 20.10.21-0ubuntu1~18.04.3；containerd 1.6.12、runc 1.1.4 | 按当前本机 apt 缓存，候选仍等于已装版本，docker-ce 无候选；未运行 apt update，不能把缓存当成远端软件源实时状态 |
| Swarm 配置 | version 3.9；overlay、secret、标签约束、global exporter、host 端口、内存限制 | 当前均已工作；仍应使用 stack deploy，不因安装 Compose V2 就改为 compose up |
| Maven 镜像插件 | 原 POM 使用 spotify dockerfile-maven-plugin 1.4.13 | 项目已归档；与新 daemon API 的兼容性必须实测，不能承诺直接跨代升级后原命令不变 |
| 当前构建 | Maven package 后执行 docker build | 绕过旧插件；升级后要检查 Buildx/BuildKit 是否齐全、基础镜像拉取、构建和 save/load |
| 容器资源与监控 | overlay2、cgroupfs、cgroup v1；应用 JVM 与监控依赖容器及宿主机资源信息 | 迁移 cgroup 或内核后应重验内存限制、OOM、JVM资源识别和监控指标 |
| 历史数据 | 90 组正式数据已在当前版本完成 | 数据继续有效；升级后新增结果须标记新环境，不能与旧环境混成同一对照组 |
| 集群运行方式 | 只有一个 Manager；MySQL 和应用单副本，demo 同宿主机运行 | 升级守护进程涉及管理和服务中断风险，不能当成无感升级 |

Docker 官方当前 Ubuntu 安装页已不列 Ubuntu 18.04；从发行版 docker.io 改装 Docker CE 还涉及冲突包与 containerd/runc 的处理。因此这里的重点是操作系统与运行时组合，而非单独升高一个 Docker 版本号。[官方 Ubuntu 安装要求](https://docs.docker.com/engine/install/ubuntu/)

现代 Docker 的 stack deploy 仍使用 Compose v3 格式，并不等同于最新 Compose specification；升级不会自动把现有 Swarm 部署变成 Compose V2 部署。[官方 Swarm 部署文档](https://docs.docker.com/engine/swarm/stack-deploy/)

Docker 29 起弃用 cgroup v1，但并非立即移除；本环境正在使用 v1。旧构建器也已弃用，迁移时应验证 BuildKit。旧 Maven 插件归档于 2022 年。这些是需要测试的兼容性因素，不是已发现本项目升级后一定失败。[Docker 弃用说明](https://docs.docker.com/engine/deprecated/)、[插件官方仓库](https://github.com/spotify/dockerfile-maven)

## 升级方案取舍

| 方案 | 建议 |
| --- | --- |
| 本次验收保持现状 | 推荐；保留已验证环境及一致的报告记录 |
| 只为 stack config 更换 CLI | 收益有限；若确需离线解析，可隔离使用兼容 CLI，但须验证输出和 API，不必因此更换整个集群 |
| Ubuntu 18.04 上强行装最新 Docker | 不推荐；不在当前官方支持组合内，还需处理软件包、内核与运行时兼容 |
| 验收后迁移到受支持 Ubuntu LTS 与受支持 Docker | 适合长期维护；例如评估 Ubuntu 24.04，再锁定经测试的 Docker 版本。它会偏离本次指导书的 Ubuntu 18.04 环境，应作为新的部署环境记录 |

若日后决定升级：先导出数据库、应用和监控镜像、secret 源文件、部署配置及私密凭据备份，并为单 Manager 的 Swarm 状态制定可恢复备份；在独立环境验证 build、save/load、stack deploy、overlay DNS、secret、MySQL持久化、6 个监控目标、两框架功能测试及小规模 JMeter；安排维护窗口，按确认过的版本迁移路径更新节点，确认最终版本一致。不要在数据目录格式可能变化后简单降级包来假定回滚成功。

本次没有进行目标版本安装演练，因此没有给出未经验证的一键升级命令或零停机承诺。
