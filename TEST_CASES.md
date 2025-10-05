# 測試案例說明

## 📊 更新後的測試案例（5 個）

### 為什麼更新？

原本的 3 個簡短評論已更換為 **5 個更長、更真實的產品評論**，原因：

1. **更真實**：模擬實際用戶的詳細評論
2. **更具挑戰性**：測試模型處理長文本的能力
3. **更豐富的上下文**：包含優缺點對比，更能測試 sentiment 判斷
4. **多語言混合**：中英文交替，測試跨語言理解能力
5. **更多數據點**：從 3 個增加到 5 個，更全面的評估

---

## 🎯 新測試案例詳情

### Test 1: 無線耳機（中文，混合情感）

```
我最近買了這款無線耳機，整體來說音質表現相當出色，低音渾厚、高音清晰。
不過使用了兩個禮拜後發現，藍牙連線經常會突然斷掉，尤其是在人多的地方更明顯，
需要重新配對才能使用，這點真的很困擾。
```

**挑戰點**：
- ✅ 包含正面評價（音質出色）
- ❌ 包含負面問題（藍牙斷線）
- 🎯 需要判斷整體情感為 negative（問題更嚴重）

**期望輸出**：
```json
{
  "sentiment": "negative",
  "product": "headphones",
  "issue": "bluetooth disconnection in crowded areas"
}
```

---

### Test 2: 機械鍵盤（英文，負面主導）

```
The mechanical keyboard I purchased has excellent build quality with a satisfying 
tactile feedback that makes typing a pleasure. However, I'm quite disappointed with 
the battery life - it only lasts about 3-4 days with the RGB lighting on, which is 
far shorter than the advertised 2 weeks. I find myself charging it constantly.
```

**挑戰點**：
- ✅ 讚美建造品質和手感
- ❌ 強烈抱怨電池續航
- 🎯 "disappointed" 表明整體為 negative

**期望輸出**：
```json
{
  "sentiment": "negative",
  "product": "keyboard",
  "issue": "short battery life"
}
```

---

### Test 3: 相機（中文，複雜情境）

```
這台相機的畫質真的沒話說，日拍的照片色彩鮮豔、細節豐富，完全達到專業水準。
但是一到晚上或光線不足的環境，對焦速度就變得超級慢，常常要對好幾次才能成功，
拍夜景或室內照片時很不方便，希望未來韌體更新能改善這個問題。
```

**挑戰點**：
- ✅ 日拍畫質優秀（正面）
- ❌ 夜拍對焦慢（負面且影響使用）
- 🎯 有具體場景描述，測試理解能力

**期望輸出**：
```json
{
  "sentiment": "negative",
  "product": "camera",
  "issue": "slow autofocus in low light"
}
```

---

### Test 4: 無線滑鼠（英文，硬體問題）

```
I've been using this wireless mouse for gaming and productivity work for the past month. 
The ergonomic design is comfortable for long sessions, and the precision is excellent 
for both gaming and design work. The only downside is that the left click button has 
started developing a double-click issue, which is frustrating during important tasks.
```

**挑戰點**：
- ✅ 人體工學好、精準度高
- ❌ 硬體故障（雙擊問題）
- 🎯 "frustrating" 表示嚴重影響使用

**期望輸出**：
```json
{
  "sentiment": "negative",
  "product": "mouse",
  "issue": "double-click hardware defect"
}
```

---

### Test 5: 智慧手錶（中文，多重問題）

```
這款智慧手錶的螢幕顯示效果很棒，在陽光下也能清楚看見，而且運動追蹤功能很準確。
可是續航力真的讓人失望，官方說可以用5天，但實際上開啟所有功能後，大概2天就要充電了。
另外充電速度也很慢，要充滿電需要將近3小時，對於經常外出的人來說很不方便。
```

**挑戰點**：
- ✅ 螢幕好、追蹤準確
- ❌ 兩個主要問題：續航短 + 充電慢
- 🎯 需要綜合多個負面因素

**期望輸出**：
```json
{
  "sentiment": "negative",
  "product": "smartwatch",
  "issue": "poor battery life and slow charging"
}
```

---

## 📈 測試案例統計

| 特徵 | 數量 |
|------|------|
| **總數** | 5 個 |
| **語言** | 3 中文、2 英文 |
| **產品類型** | 5 種不同產品 |
| **平均長度** | ~100-120 字 |
| **情感分布** | 全部 negative（混合評價） |
| **問題複雜度** | 從單一到多重問題 |

---

## 🎓 Context Engineering 測試目標

### Context A（Baseline）
預期表現：**60-70%**
- 可能無法正確識別複雜情感
- 可能產生不符合 schema 的輸出
- 可能混淆 positive 評價與整體 sentiment

### Context B（Rules-based）
預期表現：**80-90%**
- 規則幫助產生正確格式
- 更好地理解 sentiment 定義
- 可能仍在複雜案例中出錯

### Context C（Few-shot）
預期表現：**90-100%**
- 從範例學習情感判斷
- 理解如何處理混合評價
- 更一致的輸出格式

---

## 🔍 評分標準

每個測試案例的輸出必須：

1. ✅ **有效的 JSON**：可解析
2. ✅ **正確的 keys**：`sentiment`, `product`, `issue`
3. ✅ **有效的 sentiment**：`positive`, `neutral`, 或 `negative`
4. ✅ **非空的 product**：識別出產品類型
5. ✅ **有效的 issue**：字串類型（可為空）

**滿分**：5/5（100%）  
**及格**：4/5（80%）

---

## 💡 實際應用意義

這些測試案例反映了真實世界的挑戰：

1. **電商評論分析**：處理複雜的用戶評價
2. **客服自動化**：識別主要問題點
3. **產品改進**：從評論中提取可操作的反饋
4. **情感分析**：理解混合情感的細微差別

---

## 🚀 使用方式

所有實驗腳本都已更新使用這些測試案例：

```bash
# 運行實驗
python context_experiment_dotenv.py

# 或使用 Responses API 版本
python context_experiment_true_responses_api.py
```

---

## 📊 期望結果對比

### 原本（3 個簡短案例）

```
Context A: 66.7% (2/3)
Context B: 100%  (3/3)
Context C: 100%  (3/3)
```

### 更新後（5 個複雜案例）

```
Context A: ~60%  (3/5) - 更具挑戰性
Context B: ~80%  (4/5) - 規則幫助不足
Context C: ~95%  (4.5-5/5) - Few-shot 顯著優勢
```

**結論**：更長、更複雜的案例能**更清楚地展現不同 context 策略的差異**！

---

**最後更新**：2025-10-05  
**案例數量**：5 個  
**平均長度**：~110 字  
**挑戰等級**：⭐⭐⭐⭐ (中高)
