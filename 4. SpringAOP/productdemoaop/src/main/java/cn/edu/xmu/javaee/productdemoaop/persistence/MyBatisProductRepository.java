package cn.edu.xmu.javaee.productdemoaop.persistence;

import cn.edu.xmu.javaee.productdemoaop.mapper.ProductPoMapper;
import cn.edu.xmu.javaee.productdemoaop.mapper.po.ProductPo;
import java.util.*;
import lombok.RequiredArgsConstructor;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.context.annotation.Profile;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

@Repository
@Profile("mybatis")
@RequiredArgsConstructor
public class MyBatisProductRepository implements ProductPoMapper {
    private final SqlSessionTemplate sql;
    private static final String NS = "lab3.";

    public Optional<ProductPo> findById(Long id) {
        return Optional.ofNullable(sql.selectOne(NS + "productById", id));
    }

    public <S extends ProductPo> S save(S entity) {
        if (entity.getId() == null) sql.insert(NS + "insertProduct", entity);
        else sql.update(NS + "updateProduct", entity);
        return entity;
    }

    public void deleteById(Long id) { sql.delete(NS + "deleteProduct", id); }

    public List<ProductPo> findByName(String name, Pageable page) {
        return sql.selectList(NS + "productsByName", Map.of("name", name,
                "offset", page.getOffset(), "limit", page.getPageSize()));
    }

    public List<ProductPo> findByShopIdAndName(Long shopId, String name, Pageable page) {
        return sql.selectList(NS + "productsByName", Map.of("shopId", shopId, "name", name,
                "offset", page.getOffset(), "limit", page.getPageSize()));
    }

    public List<ProductPo> findByIdIn(List<Long> ids) {
        if (ids.isEmpty()) return List.of();
        return sql.selectList(NS + "productsByIds", ids);
    }
}
