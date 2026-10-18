package cn.edu.xmu.javaee.productdemoaop.persistence;

import cn.edu.xmu.javaee.productdemoaop.mapper.GoodsPoMapper;
import cn.edu.xmu.javaee.productdemoaop.mapper.po.GoodsPo;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Repository;

@Repository
@Profile("mybatis")
@RequiredArgsConstructor
public class MyBatisGoodsRepository implements GoodsPoMapper {
    private final SqlSessionTemplate sql;
    public List<GoodsPo> findByProductId(Long id) {
        return sql.selectList("lab3.goodsByProduct", id);
    }
}
