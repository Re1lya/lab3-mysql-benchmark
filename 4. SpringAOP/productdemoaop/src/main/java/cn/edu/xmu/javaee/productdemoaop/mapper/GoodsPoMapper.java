package cn.edu.xmu.javaee.productdemoaop.mapper;

import cn.edu.xmu.javaee.productdemoaop.mapper.po.GoodsPo;
import org.springframework.data.repository.Repository;
import org.springframework.context.annotation.Profile;

import java.util.List;

@Profile("!mybatis")
public interface GoodsPoMapper extends Repository<GoodsPo, Long> {
    List<GoodsPo> findByProductId(Long productId);

}
