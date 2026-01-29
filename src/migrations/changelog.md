## [2024-11-06] -Se modifico la columna informacion_adicional en la tabla cliente_cv a null

**SQL**

```sql
ALTER TABLE `cliente_cv` CHANGE `Informacion_adicional` `Informacion_adicional` VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;

ALTER TABLE `proveedor_cv` CHANGE `Información_adicional` `Información_adicional` VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;
ALTER TABLE `estaciones_cv` CHANGE `Información_adicional` `Información_adicional` VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL;


```






## [2024-11-06] - Se agrego la columna PermisoClienteOProveedor a la tabla estaciones_cv despues de la columna Información_adicional

**SQL**

```sql
ALTER TABLE `estaciones_cv` ADD `PermisoClienteOProveedor` VARCHAR(150) NOT NULL AFTER `Información_adicional`;
```




## [2024-11-03] - Se cambio la  estructura de la columa cfdis_comercializador de DATE a DATETIME

**SQL**

```sql


ALTER TABLE `cfdis_comercializador` CHANGE `FechaYHoraTransaccion` `FechaYHoraTransaccion` DATETIME NOT NULL;

```

## [2024-11-03] - Se agrego la columna Id_PRODUCTO_fk a la tabla tanques después de la columna codigo

**SQL**

```sql


ALTER TABLE `cfdis_comercializador` CHANGE `FechaYHoraTransaccion` `FechaYHoraTransaccion` DATETIME NOT NULL;

ALTER TABLE `descargas_distribuidor` CHANGE `ArchivoFacturaNombreXML` `ArchivoFacturaNombreXML` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL;
ALTER TABLE `tanque` ADD `Id_PRODUCTO_fk` INT NOT NULL AFTER `codigo`;

```

## [2024-10-31] - Cambio en la longitud en la columna mensaje de la tabla eventos_distribuidor

**SQL**

```sql
ALTER TABLE `eventos_distribuidor` CHANGE `mensaje` `mensaje` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL;
```

## [2024-10-31] -  

**SQL**

```sql
ALTER TABLE `carga_distribuidor` CHANGE `id_entregas_fk` `id_entregas_fk` INT(11) NULL;
ALTER TABLE `cargas_comercializador` CHANGE `id_entregas_fk` `id_entregas_fk` INT(11) NULL;
UPDATE `cargas_comercializador` SET `Id_cfdi_comercializador_fk` = NULL WHERE `cargas_comercializador`.`Id` = 1;
 

UPDATE `carga_distribuidor` SET id_entregas_fk = NULL;
 

UPDATE `carga_distribuidor` SET Id_cfdi_distribuidor_fk = NULL;
DELETE FROM `cfdis_distribuidor` WHERE `cfdis_distribuidor`.`Id_CFDIS_distribuidor` = 1;
DELETE FROM `cfdis_distribuidor` WHERE `cfdis_distribuidor`.`Id_CFDIS_distribuidor` = 2;
DELETE FROM `cfdis_distribuidor` WHERE `cfdis_distribuidor`.`Id_CFDIS_distribuidor` = 3;
DELETE FROM `cfdis_distribuidor` WHERE `cfdis_distribuidor`.`Id_CFDIS_distribuidor` = 4;
DELETE FROM `cfdis_distribuidor` WHERE `cfdis_distribuidor`.`Id_CFDIS_distribuidor` = 5;
DELETE FROM `cfdis_distribuidor` WHERE `cfdis_distribuidor`.`Id_CFDIS_distribuidor` = 6;

```





## [2024-10-30] - Se agrego la columna descripción a la tabla roles después de NombreRol

**SQL**

```sql
ALTER TABLE `roles` ADD `Descripcion` VARCHAR(400) NOT NULL AFTER `NombreRol`;

```


## [2024-10-30] - Cambio de tipo de dato de la columna UsuarioResponsable de la tabla eventos_distribuidor

**SQL**

```sql
ALTER TABLE `eventos_distribuidor` CHANGE `UsuarioResponsable` `UsuarioResponsable` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL;

ALTER TABLE `eventos_comercializador` CHANGE `UsuarioResponsable` `UsuarioResponsable` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL;
UPDATE `cargas_comercializador` SET `Id_cfdi_comercializador_fk` = '0' WHERE `cargas_comercializador`.`Id` = 1;


```



## [2024-10-22] - Script para reiniciar tablas de reportes

**SQL**

```sql
DELETE FROM producto_tanque_reportedevolumenmensual;
DELETE FROM tanque_existencias_recepciones_entregas;
DELETE FROM reportevolumenmensual_recepciones_m_entregas_m;
DELETE FROM existencias;
DELETE FROM recepciones;
DELETE FROM entregas;
DELETE FROM recepciones_m;
DELETE FROM entregas_m;
DELETE FROM reportedevolumenmensual;
DELETE FROM cargas_comercializador;
DELETE FROM descargas_comercializador;
DELETE FROM carga_distribuidor;
DELETE FROM descargas_distribuidor;
DELETE FROM cfdis_distribuidor;
DELETE FROM cfdis_comercializador;
ALTER TABLE producto_tanque_reportedevolumenmensual AUTO_INCREMENT = 1;
ALTER TABLE tanque_existencias_recepciones_entregas AUTO_INCREMENT = 1;
ALTER TABLE existencias AUTO_INCREMENT = 1;
ALTER TABLE recepciones AUTO_INCREMENT = 1;
ALTER TABLE entregas AUTO_INCREMENT = 1;
ALTER TABLE recepciones_m AUTO_INCREMENT = 1;
ALTER TABLE entregas_m AUTO_INCREMENT = 1;
ALTER TABLE reportedevolumenmensual AUTO_INCREMENT = 1;
ALTER TABLE reportevolumenmensual_recepciones_m_entregas_m AUTO_INCREMENT = 1;
ALTER TABLE cargas_comercializador AUTO_INCREMENT = 1;
ALTER TABLE descargas_comercializador AUTO_INCREMENT = 1;
ALTER TABLE carga_distribuidor AUTO_INCREMENT = 1;
ALTER TABLE descargas_distribuidor AUTO_INCREMENT = 1;
ALTER TABLE cfdis_distribuidor AUTO_INCREMENT = 1;
ALTER TABLE cfdis_comercializador AUTO_INCREMENT = 1;
```

## [2024-10-22] - Base de dato funcional y actual del proyecto