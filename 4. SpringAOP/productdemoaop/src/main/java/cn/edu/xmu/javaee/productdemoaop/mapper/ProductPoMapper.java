package cn.edu.xmu.javaee.productdemoaop.mapper;

import cn.edu.xmu.javaee.productdemoaop.mapper.po.ProductPo;
import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.Repository;
import org.springframework.context.annotation.Profile;
import java.util.Optional;

import java.util.List;

@Profile("!mybatis")
public interface ProductPoMapper extends Repository<ProductPo, Long> {
    Optional<ProductPo> findById(Long id);
    <S extends ProductPo> S save(S entity);
    void deleteById(Long id);
    List<ProductPo> findByName(String name, Pageable pageable);
    List<ProductPo> findByShopIdAndName(Long shopId, String name, Pageable pageable);
    List<ProductPo> findByIdIn(List<Long> ids);

}
