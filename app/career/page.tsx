"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, User, Bot, Sparkles, ArrowLeft } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Message {
    role: 'user' | 'model';
    content: string;
}

export default function CareerPage() {
    const router = useRouter();
    const [messages, setMessages] = useState<Message[]>([
        { role: 'model', content: 'Halo! Saya asisten karir AI Anda. Ada yang bisa saya bantu mengenai rencana karir atau rekomendasi pelatihan?' }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [occupation, setOccupation] = useState<any>(null);

    useEffect(() => {
        const occStr = localStorage.getItem("selectedOccupation");
        if (occStr) {
            setOccupation(JSON.parse(occStr));
        }
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const newMessages = [...messages, { role: 'user', content: input } as Message];
        setMessages(newMessages);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: input, history: newMessages }),
            });
            const json = await res.json();

            setMessages([...newMessages, { role: 'model', content: json.response || "Maaf, terjadi kesalahan." }]);
        } catch (err) {
            console.error(err);
            setMessages([...newMessages, { role: 'model', content: "Maaf, saya tidak dapat terhubung saat ini." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen bg-[#0f1117] text-white overflow-hidden">
            {/* Sidebar Info (Hidden on mobile for now) */}
            <div className="hidden md:flex flex-col w-80 bg-[#1c1f2b] border-r border-gray-800 p-6">
                <button onClick={() => router.push("/results")} className="flex items-center text-gray-500 hover:text-white mb-8">
                    <ArrowLeft className="w-4 h-4 mr-2" /> Pilih Ulang
                </button>

                {occupation && (
                    <div className="mb-8 p-6 rounded-2xl bg-gradient-to-br from-orange-500/10 to-yellow-500/5 border border-orange-500/20">
                        <span className="text-xs font-bold text-orange-400 uppercase tracking-wider">Target Karir</span>
                        <h2 className="text-2xl font-bold mt-2 mb-1">{occupation.nama}</h2>
                        <div className="text-sm text-gray-500 font-mono">{occupation.id}</div>
                    </div>
                )}

                <div className="mt-auto">
                    <div className="p-4 rounded-xl bg-[#252a3d] border border-gray-700">
                        <h4 className="font-bold flex items-center mb-2">
                            <Sparkles className="w-4 h-4 text-yellow-400 mr-2" />
                            Tips
                        </h4>
                        <p className="text-xs text-gray-400 leading-relaxed">
                            Tanyakan tentang roadmap belajar, sertifikasi yang dibutuhkan, atau simulasi interview untuk posisi ini.
                        </p>
                    </div>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                <header className="p-4 md:p-6 border-b border-gray-800 bg-[#0f1117]/80 backdrop-blur-md sticky top-0 z-10">
                    <h1 className="text-xl font-bold flex items-center">
                        <span className="w-2 h-2 rounded-full bg-green-500 mr-3 animate-pulse"></span>
                        Career Assistant
                    </h1>
                </header>

                <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
                    {messages.map((msg, idx) => (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            key={idx}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`max-w-[80%] md:max-w-2xl flex items-start space-x-4 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-orange-600' : 'bg-gray-700'
                                    }`}>
                                    {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                                </div>

                                <div className={`p-4 rounded-2xl ${msg.role === 'user'
                                        ? 'bg-orange-600 text-white rounded-tr-none'
                                        : 'bg-[#252a3d] text-gray-200 rounded-tl-none border border-gray-700'
                                    }`}>
                                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="flex items-center space-x-2 bg-[#252a3d] px-4 py-3 rounded-2xl rounded-tl-none border border-gray-700 ml-12">
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></span>
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="p-4 md:p-6 bg-[#0f1117] border-t border-gray-800">
                    <form onSubmit={handleSend} className="relative max-w-4xl mx-auto">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ketik pesan Anda..."
                            className="w-full bg-[#1c1f2b] border border-gray-700 rounded-2xl pl-6 pr-14 py-4 focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500 transition-all text-white placeholder-gray-500"
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="absolute right-3 top-3 p-2 bg-orange-600 hover:bg-orange-500 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <Send className="w-5 h-5 text-white" />
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
