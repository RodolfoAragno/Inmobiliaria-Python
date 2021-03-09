BEGIN;
--
-- Add field expensas_ext to mescontrato
--
ALTER TABLE "contratos_mescontrato" ADD COLUMN "expensas_ext" numeric(12, 2) DEFAULT '0.00' NULL;
ALTER TABLE "contratos_mescontrato" ALTER COLUMN "expensas_ext" DROP DEFAULT;
COMMIT;
BEGIN;
--
-- Add field oficina to contrato
--
ALTER TABLE "contratos_contrato" ADD COLUMN "oficina" varchar(4) DEFAULT 'SAFE' NOT NULL;
ALTER TABLE "contratos_contrato" ALTER COLUMN "oficina" DROP DEFAULT;
COMMIT;
BEGIN;
--
-- Add field cobrar_agua_propietario to contrato
--
ALTER TABLE "contratos_contrato" ADD COLUMN "cobrar_agua_propietario" boolean DEFAULT false NOT NULL;
ALTER TABLE "contratos_contrato" ALTER COLUMN "cobrar_agua_propietario" DROP DEFAULT;
--
-- Add field cobrar_api_propietariooo to contrato
--
ALTER TABLE "contratos_contrato" ADD COLUMN "cobrar_api_propietariooo" boolean DEFAULT false NOT NULL;
ALTER TABLE "contratos_contrato" ALTER COLUMN "cobrar_api_propietariooo" DROP DEFAULT;
--
-- Add field cobrar_tasa_propietario to contrato
--
ALTER TABLE "contratos_contrato" ADD COLUMN "cobrar_tasa_propietario" boolean DEFAULT false NOT NULL;
ALTER TABLE "contratos_contrato" ALTER COLUMN "cobrar_tasa_propietario" DROP DEFAULT;
COMMIT;
