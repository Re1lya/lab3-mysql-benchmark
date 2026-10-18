package cn.edu.xmu.javaee.productdemoaop.mapper;

import cn.edu.xmu.javaee.productdemoaop.mapper.po.OnSalePo;
import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.Repository;
import org.springframework.context.annotation.Profile;

import java.time.LocalDateTime;
import java.util.List;

@Profile("!mybatis")
public interface OnSalePoMapper extends Repository<OnSalePo, Long> {

    List<OnSalePo> findByProductIdEqualsAndBeginTimeBeforeAndEndTimeAfter(Long productId, LocalDateTime beginTime, LocalDateTime endTime, Pageable pageable);

}
