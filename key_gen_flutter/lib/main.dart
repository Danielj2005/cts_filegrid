import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
    runApp(const KeyGenApp());
}

class KeyGenApp extends StatelessWidget {
    const KeyGenApp({super.key});

    @override
    Widget build(BuildContext context) {
        return MaterialApp(
            debugShowCheckedModeBanner: false,
            title: 'CTS Key Generator',
            theme: ThemeData.dark().copyWith(
                scaffoldBackgroundColor: const Color(0xFF090B11),
                colorScheme: ColorScheme.dark(
                primary: const Color(0xFF00FF9D),
                secondary: const Color(0xFF10B981),
                ),
                textTheme: ThemeData.dark().textTheme.apply(
                    bodyColor: const Color(0xFFE5E7EB),
                    displayColor: const Color(0xFFE5E7EB),
                    ),
            ),
            home: const KeyGenPage(),
        );
    }
}

class KeyGenPage extends StatefulWidget {
    const KeyGenPage({super.key});

    @override
    State<KeyGenPage> createState() => _KeyGenPageState();
}

class _KeyGenPageState extends State<KeyGenPage> {
    final TextEditingController _hwidController = TextEditingController();
    String _generatedKey = '';

    static const String _salt = 'CTS_PRO_2026_SECURITY_99';

    void _generateKey() {
        final hwid = _hwidController.text.trim();
        if (hwid.isEmpty) {
            _showSnack('Por favor ingresa un HWID válido.');
            return;
        }

        final bytes = utf8.encode('$hwid$_salt');
        final digest = md5.convert(bytes).toString().toUpperCase().substring(0, 12);

        setState(() {
            _generatedKey = digest;
        });
    }

    void _copyKey() {
        if (_generatedKey.isEmpty) {
            _showSnack('No hay key para copiar.');
            return;
        }

        Clipboard.setData(ClipboardData(text: _generatedKey));
        _showSnack('Key copiada al portapapeles.');
    }

    void _showSnack(String message) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text(message),
                backgroundColor: const Color(0xFF111827),
                behavior: SnackBarBehavior.floating,
            ),
        );
    }

    @override
    Widget build(BuildContext context) {
        return Scaffold(
        body: SafeArea(
            child: Center(
            child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 860),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                    Container(
                        padding: const EdgeInsets.all(32),
                        decoration: BoxDecoration(
                        color: const Color(0xFF0F172A).withOpacity(0.96),
                        borderRadius: BorderRadius.circular(32),
                        border: Border.all(color: const Color(0x2584A3B8)),
                        boxShadow: [
                            BoxShadow(
                            color: const Color(0x260F172A),
                            blurRadius: 40,
                            offset: const Offset(0, 20),
                            ),
                        ],
                        ),
                        child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                            Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                                Container(
                                width: 64,
                                height: 64,
                                decoration: BoxDecoration(
                                    color: const Color(0xFF0F172A),
                                    borderRadius: BorderRadius.circular(20),
                                ),
                                child: Image.asset('assets/images/logo.png', fit: BoxFit.contain),
                                ),
                                const SizedBox(width: 20),
                                Expanded(
                                child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: const [
                                    Text('Generador de Keys CTS',
                                        style: TextStyle(
                                            color: Color(0xFF00FF9D),
                                            fontSize: 32,
                                            fontWeight: FontWeight.w800,
                                        )),
                                    SizedBox(height: 8),
                                    Text(
                                        'Interfaz móvil con diseño elegante para generar licencias sin conexión.',
                                        style: TextStyle(color: Color(0xFF94A3B8), fontSize: 16, height: 1.6),
                                    ),
                                    ],
                                ),
                                ),
                            ],
                            ),
                        const SizedBox(height: 32),
                        const Text('HWID del cliente', style: TextStyle(color: Color(0xFFCBD5E1), fontWeight: FontWeight.w600)),
                        const SizedBox(height: 12),
                        TextField(
                          controller: _hwidController,
                          style: const TextStyle(color: Color(0xFFE2E8F0)),
                          decoration: InputDecoration(
                            filled: true,
                            fillColor: const Color(0xFF0F172A),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: BorderSide(color: const Color(0x2984A3B8)),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: const BorderSide(color: Color(0xFF00FF9D)),
                            ),
                            hintText: 'Pega el HWID aquí',
                            hintStyle: const TextStyle(color: Color(0xFF94A3B8)),
                          ),
                        ),
                        const SizedBox(height: 24),
                        ElevatedButton(
                          onPressed: _generateKey,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF00FF9D),
                            foregroundColor: const Color(0xFF0F172A),
                            padding: const EdgeInsets.symmetric(vertical: 18),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                          ),
                          child: const Text('GENERAR KEY', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
                        ),
                        const SizedBox(height: 24),
                        const Text('Key generada', style: TextStyle(color: Color(0xFFCBD5E1), fontWeight: FontWeight.w600)),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF0F172A),
                                  borderRadius: BorderRadius.circular(24),
                                  border: Border.all(color: const Color(0x2984A3B8)),
                                ),
                                child: Text(
                                  _generatedKey.isEmpty ? 'Aquí aparecerá la key' : _generatedKey,
                                  style: TextStyle(
                                    color: _generatedKey.isEmpty ? const Color(0xFF94A3B8) : const Color(0xFF7CFC00),
                                    fontFamily: 'Courier New',
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 14),
                            ElevatedButton(
                              onPressed: _copyKey,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF111827),
                                foregroundColor: const Color(0xFFE2E8F0),
                                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                              ),
                              child: const Text('COPIAR'),
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        const Text(
                          'La key se genera usando el HWID + el salt privado de CTS. Úsala en el sistema de activación.',
                          style: TextStyle(color: Color(0xFF94A3B8), height: 1.6),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.all(26),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0F172A).withOpacity(0.94),
                      borderRadius: BorderRadius.circular(32),
                      border: Border.all(color: const Color(0x1A94A3B8)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text('Consejo de uso:', style: TextStyle(color: Color(0xFFF8FAFC), fontWeight: FontWeight.w700, fontSize: 16)),
                        SizedBox(height: 16),
                        Text('• Ingresa el HWID del cliente en el campo superior.', style: TextStyle(color: Color(0xFF94A3B8), height: 1.7)),
                        SizedBox(height: 8),
                        Text('• Presiona GENERAR KEY para crear la licencia.', style: TextStyle(color: Color(0xFF94A3B8), height: 1.7)),
                        SizedBox(height: 8),
                        Text('• Verifica que la key aparezca y usa COPIAR para compartirla.', style: TextStyle(color: Color(0xFF94A3B8), height: 1.7)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
