# 🔐 Implementação de Hash de Senhas

## Alterações Realizadas

### 1. AuthService (`services/auth_service.py`)
- ✅ Atualizado `hash_password()` - Hash seguro com pbkdf2:sha256
- ✅ Atualizado `verify_password()` - Compara senhas com hash seguro
- ✅ Usa `werkzeug.security` (já vem com Flask)
- ❌ Removido SHA256 simples (inseguro)

### 2. Modelo Cliente (`models.py`)
- ✅ Método `set_password(senha)` - Usa `AuthService.hash_password()`
- ✅ Método `check_password(senha)` - Usa `AuthService.verify_password()`
- ✅ Centralizado no AuthService para consistência

### 2. Algoritmo de Hash
- **Método**: `pbkdf2:sha256` (via `AuthService`)
- **Segurança**: Produção-ready, recomendado pela OWASP
- **Características**:
  - Iterações: 260.000+ (padrão werkzeug)
  - Salt automático único por senha
  - Resistente a ataques de força bruta
  - Compatível com GDPR/LGPD

### 3. Centralização
Todos os métodos de hash de senha estão centralizados no `AuthService`:
- `AuthService.hash_password(senha)` - Gera hash seguro
- `AuthService.verify_password(senha, hash)` - Verifica senha

Modelos usam o `AuthService` para garantir consistência.
```
Antes: minha_senha_123
Depois: pbkdf2:sha256:260000$abc123xyz$hash_muito_longo...
```

## ⚠️ Migração de Senhas Existentes

Se você já tem clientes cadastrados com senhas em texto plano:

```bash
# 1. Backup do banco de dados
cp propaganda.db propaganda.db.backup

# 2. Execute o script de migração
cd server
python migrate_passwords.py

# 3. Confirme quando solicitado
```

**IMPORTANTE**: Após a migração, as senhas originais não podem ser recuperadas!

## 🧪 Testando

### Teste Manual
1. Cadastre um novo cliente
2. Verifique o banco de dados:
```sql
SELECT email, senha FROM clientes;
```
3. A senha deve estar em formato hash (começando com `pbkdf2:sha256:`)
4. Teste o login com a senha original

### Teste Automático
```bash
pytest tests/test_services.py::TestClienteService -v
```

## 🔒 Benefícios de Segurança

1. **Senhas nunca são armazenadas em texto plano**
2. **Salt único por senha** - Mesmo senhas iguais geram hashes diferentes
3. **Resistente a rainbow tables** - Salt protege contra ataques pré-computados
4. **Custo computacional alto** - Dificulta ataques de força bruta
5. **Conformidade LGPD/GDPR** - Proteção adequada de dados sensíveis

## 📝 Como Funciona

### Registro de Cliente
```python
# Serviço recebe senha em texto plano
cliente.set_password("minha_senha_123")
# Armazena: pbkdf2:sha256:260000$salt$hash
```

### Login de Cliente
```python
# Usuário envia senha em texto plano
cliente.check_password("minha_senha_123")
# Compara com hash armazenado (retorna True/False)
```

## 🛡️ Boas Práticas Implementadas

- ✅ Hash unidirecional (não pode ser revertido)
- ✅ Salt único automático
- ✅ Algoritmo moderno (pbkdf2:sha256)
- ✅ Sem senhas em logs ou memória
- ✅ Proteção contra timing attacks
- ✅ Compatível com padrões de segurança

## 🚨 Notas de Segurança

1. **Nunca logue senhas** - Nem em texto plano, nem em hash
2. **Use HTTPS em produção** - Protege senhas em trânsito
3. **Senhas esquecidas = reset** - Não há como "recuperar" senhas
4. **Mínimo 6 caracteres** - Já validado no formulário

## 📚 Referências

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Werkzeug Security](https://werkzeug.palletsprojects.com/en/3.0.x/utils/#module-werkzeug.security)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
