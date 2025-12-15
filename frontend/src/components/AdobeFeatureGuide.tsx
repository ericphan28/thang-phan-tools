/**
 * Adobe PDF Feature Guide Component
 * Shows contextual help with examples for each feature
 */

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { 
  HelpCircle, 
  CheckCircle, 
  AlertCircle, 
  Lightbulb,
  Code,
  FileText,
  ArrowRight,
  X
} from 'lucide-react';

interface GuideExample {
  scenario: string;
  steps: string[];
  result: string;
}

interface GuideTip {
  icon: 'check' | 'alert' | 'lightbulb';
  text: string;
}

interface CodeExample {
  title: string;
  code: string;
  language: string;
}

interface FeatureGuideData {
  title: string;
  color: string;
  description: string;
  whenToUse: string[];
  example: GuideExample;
  tips: GuideTip[];
  codeExample?: CodeExample;
}

const FEATURE_GUIDES: Record<string, FeatureGuideData> = {
  watermark: {
    title: 'Đóng Dấu Mờ (Watermark)',
    color: 'blue',
    description: 'Thêm watermark văn bản hoặc hình ảnh lên tất cả trang PDF để bảo vệ bản quyền và định danh tài liệu.',
    whenToUse: [
      'Cần bảo vệ bản quyền tài liệu (báo cáo, presentation, ebook)',
      'Đánh dấu tài liệu nội bộ (DRAFT, CONFIDENTIAL)',
      'Branding tài liệu với logo công ty',
      'Tạo chứng từ không thể sao chép (hóa đơn, hợp đồng)'
    ],
    example: {
      scenario: 'Công ty cần gửi báo cáo tài chính Q4 cho khách hàng nhưng đánh dấu "CONFIDENTIAL" để tránh leak.',
      steps: [
        'Upload file report-q4.pdf',
        'Chọn Watermark: Text = "CONFIDENTIAL"',
        'Điều chỉnh opacity = 0.3 (mờ nhẹ)',
        'Chọn vị trí = Diagonal (chéo giữa trang)',
        'Click "Add Watermark"'
      ],
      result: 'File mới có dòng chữ "CONFIDENTIAL" mờ chéo trên mỗi trang, rõ ràng nhưng không che nội dung.'
    },
    tips: [
      {
        icon: 'check',
        text: 'Dùng opacity 0.2-0.4 để watermark rõ nhưng không che nội dung quan trọng'
      },
      {
        icon: 'alert',
        text: 'Watermark văn bản dễ bị xóa hơn watermark ảnh (dùng logo PNG với background trong suốt)'
      },
      {
        icon: 'lightbulb',
        text: 'Với tài liệu quan trọng: kết hợp Watermark + Protect PDF để tăng bảo mật'
      }
    ]
  },
  combine: {
    title: 'Gộp PDF (Combine)',
    color: 'green',
    description: 'Ghép nhiều file PDF thành một file duy nhất theo thứ tự bạn chọn.',
    whenToUse: [
      'Gộp nhiều chương của một báo cáo thành file hoàn chỉnh',
      'Kết hợp hồ sơ ứng tuyển (CV + certificates + portfolio)',
      'Tạo ebook từ nhiều chapter riêng lẻ',
      'Merge các trang scan thành một tài liệu duy nhất'
    ],
    example: {
      scenario: 'HR cần tạo hồ sơ nhân viên hoàn chỉnh từ: CV + bằng cấp + hợp đồng.',
      steps: [
        'Upload 3 files: cv.pdf, degree.pdf, contract.pdf',
        'Sắp xếp thứ tự: CV → Degree → Contract (drag & drop)',
        'Click "Combine PDFs"',
        'Tải file employee-full-profile.pdf'
      ],
      result: 'Một file PDF duy nhất với CV ở trang 1-2, bằng cấp trang 3-4, hợp đồng trang 5-10.'
    },
    tips: [
      {
        icon: 'check',
        text: 'Đặt tên file theo quy tắc: 01-intro.pdf, 02-body.pdf để dễ sắp xếp'
      },
      {
        icon: 'alert',
        text: 'File gộp sẽ có kích thước bằng tổng các file gốc (check dung lượng trước khi gửi email)'
      },
      {
        icon: 'lightbulb',
        text: 'Sau khi gộp, dùng Linearize để tối ưu cho việc xem online'
      }
    ]
  },
  split: {
    title: 'Tách PDF (Split)',
    color: 'orange',
    description: 'Chia một file PDF lớn thành nhiều file nhỏ theo trang hoặc khoảng trang.',
    whenToUse: [
      'Tách chapter từ ebook dày để đọc từng phần',
      'Chia hồ sơ đa người thành các file riêng biệt',
      'Extract trang cụ thể từ báo cáo dài (VD: trang 5-10)',
      'Giảm kích thước file để gửi email (split thành nhiều phần nhỏ)'
    ],
    example: {
      scenario: 'Giáo viên có file đề thi 50 trang (mỗi đề 5 trang) cần tách thành 10 file riêng.',
      steps: [
        'Upload file exam-all.pdf (50 trang)',
        'Chọn Split Mode: "Page Ranges"',
        'Nhập ranges: "1-5, 6-10, 11-15, ..." (hoặc dùng Auto Split Every 5 Pages)',
        'Click "Split PDF"',
        'Tải về file ZIP chứa 10 file: part-1.pdf, part-2.pdf, ...'
      ],
      result: '10 file PDF riêng biệt, mỗi file 5 trang, ready để phát cho học sinh.'
    },
    tips: [
      {
        icon: 'check',
        text: 'Dùng "Split Every N Pages" nếu chia đều (VD: mỗi 10 trang)'
      },
      {
        icon: 'alert',
        text: 'Kiểm tra số trang trước khi split (dùng PDF viewer để đếm chính xác)'
      },
      {
        icon: 'lightbulb',
        text: 'Kết hợp với Watermark: tách trước → watermark từng phần khác nhau'
      }
    ]
  },
  protect: {
    title: 'Bảo Mật PDF (Protect)',
    color: 'red',
    description: 'Đặt mật khẩu và giới hạn quyền trên PDF (in, copy, chỉnh sửa).',
    whenToUse: [
      'Gửi hợp đồng/báo cáo nhạy cảm cần mật khẩu để mở',
      'Ngăn người khác copy nội dung (bản quyền)',
      'Chặn chỉnh sửa tài liệu (hóa đơn, chứng từ)',
      'Cho phép xem nhưng không cho in (bảo vệ tài liệu đào tạo)'
    ],
    example: {
      scenario: 'Công ty gửi proposal cho client, muốn họ xem được nhưng không copy/in.',
      steps: [
        'Upload file proposal.pdf',
        'Chọn Permission Password: "view123"',
        'Uncheck quyền: "Print" và "Copy Content"',
        'Check quyền: "View Only"',
        'Click "Protect PDF"'
      ],
      result: 'Client mở file bằng mật khẩu "view123", xem được nội dung nhưng không in/copy được.'
    },
    tips: [
      {
        icon: 'check',
        text: 'User Password: mở file | Owner Password: thay đổi permissions'
      },
      {
        icon: 'alert',
        text: 'PDF password có thể bị crack nếu yếu (dùng 12+ ký tự, bao gồm số + chữ + ký tự đặc biệt)'
      },
      {
        icon: 'lightbulb',
        text: 'Với tài liệu cực nhạy cảm: Protect + Watermark + Electronic Seal (3 lớp bảo mật)'
      }
    ]
  },
  linearize: {
    title: 'Tối Ưu Web (Linearize)',
    color: 'purple',
    description: 'Tối ưu hóa PDF để load nhanh trên web (fast web view), trang đầu hiển thị ngay không cần tải hết file.',
    whenToUse: [
      'PDF dùng để xem online (website, portal)',
      'Tài liệu dài cần preview nhanh (catalog, ebook)',
      'Giảm thời gian loading cho người dùng di động',
      'Cải thiện UX cho web app hiển thị PDF'
    ],
    example: {
      scenario: 'Website hiển thị product catalog 100 trang, khách hàng phải đợi 30s mới thấy trang đầu.',
      steps: [
        'Upload file catalog.pdf (20MB, 100 trang)',
        'Click "Linearize PDF"',
        'Tải file catalog-optimized.pdf',
        'Upload lên website'
      ],
      result: 'Khách mở catalog → trang đầu hiện ngay sau 2s, tiếp tục load background các trang sau.'
    },
    tips: [
      {
        icon: 'check',
        text: 'File sau linearize chỉ tăng ~1-2% dung lượng nhưng UX cải thiện đáng kể'
      },
      {
        icon: 'alert',
        text: 'Chỉ cần thiết cho file >2MB và >10 trang (file nhỏ không cần optimize)'
      },
      {
        icon: 'lightbulb',
        text: 'Workflow tối ưu: Combine → Linearize → upload web (đảm bảo file vừa gọn vừa nhanh)'
      }
    ]
  },
  autotag: {
    title: 'Accessibility (Auto-Tag)',
    color: 'indigo',
    description: 'Tự động thêm structural tags để PDF hỗ trợ screen readers và tuân thủ chuẩn accessibility (WCAG).',
    whenToUse: [
      'PDF cho người khuyết tật (blind/low vision users)',
      'Tuân thủ quy định pháp lý (ADA, Section 508)',
      'Nộp tài liệu chính phủ (yêu cầu accessible)',
      'Cải thiện SEO (Google đọc được cấu trúc PDF)'
    ],
    example: {
      scenario: 'Trường học cần publish báo cáo thường niên lên website, phải đảm bảo accessibility cho mọi người.',
      steps: [
        'Upload file annual-report.pdf (chưa có tags)',
        'Click "Auto-Tag PDF"',
        'Hệ thống phân tích: headings, paragraphs, lists, tables',
        'Tải file annual-report-tagged.pdf'
      ],
      result: 'File mới có tags, screen reader đọc được: "Heading 1: Annual Report 2024, Paragraph: ..."'
    },
    tips: [
      {
        icon: 'check',
        text: 'Auto-tagging đạt ~80-90% chính xác, luôn kiểm tra lại bằng Adobe Acrobat Pro'
      },
      {
        icon: 'alert',
        text: 'File scan/image-based PDF cần OCR trước khi auto-tag (nếu không sẽ thiếu text content)'
      },
      {
        icon: 'lightbulb',
        text: 'Compliance checklist: Auto-Tag → Test với NVDA/JAWS screen reader → Adjust nếu cần'
      }
    ]
  },
  generate: {
    title: 'Document Generation',
    color: 'teal',
    description: 'Tạo PDF từ Word template (.docx) + JSON data. Tự động replace placeholders {{name}}, {{date}}, ... với dữ liệu thực.',
    whenToUse: [
      'Tạo hàng loạt certificates với tên khác nhau',
      'Generate hóa đơn/hợp đồng từ database',
      'Mail merge: tạo nhiều letters cá nhân hóa',
      'Automation: template + API data → PDF tự động'
    ],
    example: {
      scenario: 'Công ty cần tạo 100 certificates cho học viên hoàn thành khóa học.',
      steps: [
        'Tạo template Word: certificate.docx với placeholders: {{studentName}}, {{courseName}}, {{date}}',
        'Upload certificate.docx',
        'Nhập JSON data (hoặc upload file):\n```json\n{\n  "studentName": "Nguyễn Văn A",\n  "courseName": "React Advanced",\n  "date": "2024-12-20"\n}\n```',
        'Click "Generate Document"',
        'Tải file certificate-final.pdf'
      ],
      result: 'PDF với "Chứng nhận Nguyễn Văn A hoàn thành React Advanced ngày 2024-12-20"'
    },
    tips: [
      {
        icon: 'check',
        text: 'Placeholder syntax: {{key}} cho text, {{#if condition}} cho logic, {{#each items}} cho loops'
      },
      {
        icon: 'alert',
        text: 'JSON keys phải match chính xác với placeholders (case-sensitive)'
      },
      {
        icon: 'lightbulb',
        text: 'Pro tip: Kết hợp với API → bulk generate 1000+ documents tự động'
      }
    ],
    codeExample: {
      title: 'Ví dụ JSON Data',
      language: 'json',
      code: `{
  "studentName": "Nguyễn Văn A",
  "courseName": "React Advanced",
  "date": "2024-12-20",
  "instructor": "John Doe",
  "grade": "A+"
}`
    }
  },
  seal: {
    title: 'Electronic Seal (Chữ Ký Số)',
    color: 'amber',
    description: 'Ký số PDF với certificate để chứng thực tính toàn vẹn và nguồn gốc tài liệu (digital signature).',
    whenToUse: [
      'Hợp đồng/công văn có giá trị pháp lý',
      'Chứng từ tài chính (hóa đơn điện tử)',
      'Submission documents (tax, legal, government)',
      'Đảm bảo tài liệu không bị chỉnh sửa sau khi ký'
    ],
    example: {
      scenario: 'Giám đốc cần ký số hợp đồng mua bán trị giá $1M để gửi cho đối tác.',
      steps: [
        'Upload file contract.pdf',
        'Upload certificate: company-seal.p12',
        'Nhập password certificate: "seal@2024"',
        'Chọn vị trí chữ ký: Bottom Right',
        'Click "Apply Seal"'
      ],
      result: 'PDF có chữ ký số với thông tin: "Signed by ABC Corp, 2024-12-20, Certificate Valid". Đối tác mở file → Adobe hiện "SIGNED AND ALL SIGNATURES ARE VALID".'
    },
    tips: [
      {
        icon: 'check',
        text: 'Certificate .p12/.pfx từ CA uy tín (Symantec, DigiCert) → chữ ký có giá trị pháp lý'
      },
      {
        icon: 'alert',
        text: 'Không share password certificate! Mỗi người/tổ chức dùng cert riêng'
      },
      {
        icon: 'lightbulb',
        text: 'Self-signed certificate (free) OK cho internal docs, nhưng external partners cần CA-issued cert'
      }
    ]
  }
};

const TipIcon = ({ icon }: { icon: 'check' | 'alert' | 'lightbulb' }) => {
  const icons = {
    check: <CheckCircle className="w-4 h-4 text-green-600" />,
    alert: <AlertCircle className="w-4 h-4 text-orange-600" />,
    lightbulb: <Lightbulb className="w-4 h-4 text-yellow-600" />
  };
  return icons[icon];
};

interface AdobeFeatureGuideProps {
  open: boolean;
  onClose: () => void;
  featureId: string;
}

export const AdobeFeatureGuide: React.FC<AdobeFeatureGuideProps> = ({
  open,
  onClose,
  featureId
}) => {
  const [activeTab, setActiveTab] = useState<'guide' | 'example' | 'tips'>('guide');
  const guide = FEATURE_GUIDES[featureId];

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (open) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent background scroll
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [open, onClose]);

  if (!open || !guide) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-4xl max-h-[90vh] m-4 bg-white rounded-lg shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex-shrink-0 px-6 py-4 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <HelpCircle className={`w-6 h-6 text-${guide.color}-600`} />
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{guide.title}</h2>
                <p className="text-sm text-gray-600 mt-1">{guide.description}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="flex-shrink-0"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex-shrink-0 px-6 border-b border-gray-200">
          <div className="flex gap-1">
            {[
              { key: 'guide', label: '📖 Hướng Dẫn' },
              { key: 'example', label: '💡 Ví Dụ' },
              { key: 'tips', label: '⚡ Tips' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === tab.key
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Tab 1: Guide */}
          {activeTab === 'guide' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                  🎯 Dùng Khi Nào?
                </h3>
                <ul className="space-y-2">
                  {guide.whenToUse.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <ArrowRight className="w-4 h-4 mt-1 text-blue-600 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Tab 2: Example */}
          {activeTab === 'example' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium mb-2 text-blue-900">📋 Tình Huống</h4>
                <p className="text-sm text-blue-800">{guide.example.scenario}</p>
              </div>

              <div>
                <h4 className="font-semibold mb-3">🔧 Các Bước Thực Hiện</h4>
                <ol className="space-y-3">
                  {guide.example.steps.map((step, idx) => (
                    <li key={idx} className="flex gap-3">
                      <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-medium">
                        {idx + 1}
                      </span>
                      <span className="text-sm text-gray-700 mt-0.5 whitespace-pre-wrap">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium mb-2 text-green-900 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  ✅ Kết Quả
                </h4>
                <p className="text-sm text-green-800">{guide.example.result}</p>
              </div>

              {/* Code Example if exists */}
              {guide.codeExample && (
                <div className="bg-gray-900 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Code className="w-4 h-4 text-green-400" />
                    <span className="text-sm font-medium text-green-400">
                      {guide.codeExample.title}
                    </span>
                  </div>
                  <pre className="text-xs text-gray-300 overflow-x-auto">
                    <code>{guide.codeExample.code}</code>
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* Tab 3: Tips */}
          {activeTab === 'tips' && (
            <div className="space-y-6">
              <div className="grid gap-4">
                {guide.tips.map((tip, idx) => (
                  <div key={idx} className="flex gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex-shrink-0 mt-0.5">
                      <TipIcon icon={tip.icon} />
                    </div>
                    <p className="text-sm text-gray-700">{tip.text}</p>
                  </div>
                ))}
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium mb-2 text-blue-900 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  📚 Tài Liệu Đầy Đủ
                </h4>
                <p className="text-sm text-blue-800 mb-2">
                  Xem hướng dẫn chi tiết tại:
                </p>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• <a href="/docs/ADOBE_USER_GUIDE_VI.md" className="underline hover:text-blue-900">Hướng dẫn tiếng Việt (10,000+ từ)</a></li>
                  <li>• <a href="/docs/ADOBE_USER_GUIDE_EN.md" className="underline hover:text-blue-900">English Guide (5,000+ words)</a></li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center text-xs text-gray-600">
            <span>🎯 Adobe PDF Services - 8 tính năng chuyên nghiệp</span>
            <span>Nhấn ESC để đóng</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Help Button Component
interface HelpButtonProps {
  onClick: () => void;
}

export const HelpButton: React.FC<HelpButtonProps> = ({ onClick }) => {
  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onClick}
      className="absolute top-4 right-4 z-10"
      title="Xem hướng dẫn chi tiết"
    >
      <HelpCircle className="w-5 h-5" />
    </Button>
  );
};
