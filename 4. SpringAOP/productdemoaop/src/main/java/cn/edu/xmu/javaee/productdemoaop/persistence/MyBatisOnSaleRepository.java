package cn.edu.xmu.javaee.productdemoaop.persistence;

import cn.edu.xmu.javaee.productdemoaop.mapper.OnSalePoMapper;
import cn.edu.xmu.javaee.productdemoaop.mapper.po.OnSalePo;
import java.util.*;
import java.time.LocalDateTime;
import lombok.RequiredArgsConstructor;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.context.annotation.Profile;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

@Repository
@Profile("mybatis")
@RequiredArgsConstructor
public class MyBatisOnSaleRepository implements OnSalePoMapper {
    private final SqlSessionTemplate sql;
    public List<OnSalePo> findByProductIdEqualsAndBeginTimeBeforeAndEndTimeAfter(
            Long id, LocalDateTime begin, LocalDateTime end, Pageable page) {
        return sql.selectList("lab3.onsalesByProduct", Map.of("id", id, "begin", begin,
                "end", end, "offset", page.getOffset(), "limit", page.getPageSize()));
    }
}
