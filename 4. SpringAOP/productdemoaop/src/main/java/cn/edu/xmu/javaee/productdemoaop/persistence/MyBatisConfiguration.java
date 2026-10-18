package cn.edu.xmu.javaee.productdemoaop.persistence;

import javax.sql.DataSource;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.context.annotation.*;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.PlatformTransactionManager;

/** Same datasource and service transaction boundaries as the JPA variant. */
@Configuration
@Profile("mybatis")
public class MyBatisConfiguration {
    @Bean
    SqlSessionFactory sqlSessionFactory(DataSource dataSource) throws Exception {
        var factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        var config = new org.apache.ibatis.session.Configuration();
        config.setMapUnderscoreToCamelCase(true);
        config.setCacheEnabled(false);
        factory.setConfiguration(config);
        factory.setMapperLocations(new PathMatchingResourcePatternResolver()
                .getResources("classpath:mybatis/*.xml"));
        return factory.getObject();
    }

    @Bean
    SqlSessionTemplate sqlSessionTemplate(SqlSessionFactory factory) {
        return new SqlSessionTemplate(factory);
    }

    @Bean
    PlatformTransactionManager transactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
