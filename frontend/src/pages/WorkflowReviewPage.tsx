import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  FileText, 
  Upload, 
  ClipboardList, 
  UserCheck, 
  Send, 
  Settings, 
  CheckCircle, 
  Archive,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

interface WorkflowStep {
  id: number;
  title: string;
  icon: any;
  description: string;
  actor: string;
  tasks: string[];
  duration: string;
  priority?: 'high' | 'medium' | 'low';
}

interface Feedback {
  stepId: number;
  type: 'like' | 'dislike' | 'comment';
  comment?: string;
}

const workflowSteps: WorkflowStep[] = [
  {
    id: 1,
    title: 'Tiếp nhận văn bản',
    icon: Upload,
    actor: 'Văn thư',
    description: 'Nhận văn bản qua bưu điện, email, fax hoặc trực tiếp',
    tasks: [
      'Kiểm tra văn bản có gửi đúng cơ quan không',
      'Kiểm tra tính nguyên vẹn và file đính kèm',
      'Đóng dấu ngày nhận',
      'Phân loại mức độ: Hỏa tốc, Khẩn, Thường'
    ],
    duration: '5-10 phút',
    priority: 'high'
  },
  {
    id: 2,
    title: 'Đăng ký vào Sổ',
    icon: ClipboardList,
    actor: 'Văn thư',
    description: 'Ghi thông tin văn bản vào sổ văn bản đến',
    tasks: [
      'Đánh số thứ tự tăng dần',
      'Ghi: Số VB, Ngày VB, Nơi gửi, Trích yếu',
      'Scan văn bản thành PDF (nếu bản giấy)',
      'Upload lên hệ thống quản lý văn bản'
    ],
    duration: '5-15 phút',
    priority: 'medium'
  },
  {
    id: 3,
    title: 'Trình Lãnh đạo',
    icon: UserCheck,
    actor: 'Văn thư → Lãnh đạo',
    description: 'Đưa văn bản cho Lãnh đạo xem và chỉ đạo',
    tasks: [
      'Sắp xếp văn bản theo mức độ ưu tiên',
      'Lãnh đạo viết ý kiến chỉ đạo',
      'Chỉ định phòng ban xử lý',
      'Xác định thời hạn hoàn thành'
    ],
    duration: '30 phút - 2 giờ',
    priority: 'high'
  },
  {
    id: 4,
    title: 'Chuyển Phòng ban',
    icon: Send,
    actor: 'Văn thư',
    description: 'Chuyển văn bản + ý kiến lãnh đạo cho phòng ban được giao',
    tasks: [
      'Chuyển văn bản kèm chỉ đạo',
      'Ghi nhận ngày chuyển và người nhận',
      'Cập nhật trạng thái trong hệ thống',
      'Nhắc việc nếu sắp hết hạn'
    ],
    duration: '5-10 phút',
    priority: 'medium'
  },
  {
    id: 5,
    title: 'Xử lý Phòng ban',
    icon: Settings,
    actor: 'Trưởng phòng + Chuyên viên',
    description: 'Nghiên cứu, xử lý nội dung và soạn thảo văn bản trả lời',
    tasks: [
      'Trưởng phòng giao cho chuyên viên',
      'Nghiên cứu nội dung, thu thập tài liệu',
      'Xử lý công việc (kiểm tra, tính toán...)',
      'Soạn thảo văn bản trả lời/báo cáo',
      'Trưởng phòng kiểm tra, ký duyệt'
    ],
    duration: 'VB thường: 10-15 ngày\nVB khẩn: 2-3 ngày\nVB hỏa tốc: trong ngày',
    priority: 'high'
  },
  {
    id: 6,
    title: 'Ký phê duyệt',
    icon: CheckCircle,
    actor: 'Lãnh đạo cơ quan',
    description: 'Xem xét và ký duyệt văn bản trả lời',
    tasks: [
      'Xem xét nội dung văn bản',
      'Yêu cầu chỉnh sửa nếu chưa đạt',
      'Ký tên và đóng dấu',
      'Trả lại văn thư để gửi đi'
    ],
    duration: '30 phút - 1 ngày',
    priority: 'high'
  },
  {
    id: 7,
    title: 'Gửi văn bản trả lời',
    icon: FileText,
    actor: 'Văn thư',
    description: 'Đăng ký và gửi văn bản trả lời ra bên ngoài',
    tasks: [
      'Đăng ký vào Sổ văn bản đi',
      'Đánh số, ký hiệu văn bản',
      'Đóng dấu xác nhận',
      'Gửi qua bưu điện, email hoặc hệ thống'
    ],
    duration: '15-30 phút',
    priority: 'medium'
  },
  {
    id: 8,
    title: 'Lưu trữ & Theo dõi',
    icon: Archive,
    actor: 'Văn thư',
    description: 'Lưu trữ văn bản và theo dõi trạng thái',
    tasks: [
      'Lưu văn bản vào tủ hồ sơ',
      'Cập nhật trạng thái "Đã xử lý"',
      'Theo dõi văn bản chưa xử lý',
      'Báo cáo định kỳ cho lãnh đạo'
    ],
    duration: '10-15 phút',
    priority: 'low'
  }
];

const documentTypes = [
  { name: 'Công văn', code: 'CV', color: 'bg-blue-500' },
  { name: 'Quyết định', code: 'QĐ', color: 'bg-purple-500' },
  { name: 'Thông báo', code: 'TB', color: 'bg-green-500' },
  { name: 'Báo cáo', code: 'BC', color: 'bg-orange-500' },
  { name: 'Tờ trình', code: 'TT', color: 'bg-red-500' },
  { name: 'Công điện', code: 'CĐ', color: 'bg-yellow-500' }
];

export default function WorkflowReviewPage() {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [activeStep, setActiveStep] = useState<number | null>(null);
  const [commentText, setCommentText] = useState('');
  const [userInfo, setUserInfo] = useState({
    name: '',
    position: '',
    department: ''
  });
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  const handleLike = (stepId: number) => {
    setFeedbacks([...feedbacks, { stepId, type: 'like' }]);
    toast.success(`Cảm ơn! Bạn đã đánh giá tốt cho bước ${stepId}`);
  };

  const handleDislike = (stepId: number) => {
    setActiveStep(stepId);
    setShowFeedbackForm(true);
  };

  const handleSubmitComment = () => {
    if (!commentText.trim()) {
      toast.error('Vui lòng nhập ý kiến của bạn');
      return;
    }
    
    if (!userInfo.name || !userInfo.position) {
      toast.error('Vui lòng nhập họ tên và chức vụ');
      return;
    }

    setFeedbacks([...feedbacks, { 
      stepId: activeStep!, 
      type: 'comment', 
      comment: commentText 
    }]);
    
    toast.success('Đã gửi góp ý thành công!');
    setCommentText('');
    setActiveStep(null);
    setShowFeedbackForm(false);
  };

  const handleExportFeedback = () => {
    const summary = {
      userInfo,
      totalSteps: workflowSteps.length,
      feedbacks: feedbacks,
      timestamp: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(summary, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `feedback_${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    toast.success('Đã xuất file góp ý!');
  };

  const getLikeCount = (stepId: number) => {
    return feedbacks.filter(f => f.stepId === stepId && f.type === 'like').length;
  };

  const getDislikeCount = (stepId: number) => {
    return feedbacks.filter(f => f.stepId === stepId && f.type === 'dislike').length;
  };

  const getComments = (stepId: number) => {
    return feedbacks.filter(f => f.stepId === stepId && f.type === 'comment');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            📋 Quy trình xử lý văn bản hành chính
          </h1>
          <p className="text-lg text-gray-600 mb-2">
            Cơ quan hành chính Nhà nước Việt Nam
          </p>
          <Badge variant="outline" className="text-sm">
            Dự thảo lần 1 - Ngày 26/12/2025
          </Badge>
        </div>

        {/* User Info Form */}
        <Card className="mb-6 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white">
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Thông tin người góp ý
            </CardTitle>
            <CardDescription className="text-blue-100">
              Vui lòng cung cấp thông tin để chúng tôi ghi nhận ý kiến của bạn
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="name">Họ và tên *</Label>
                <Input
                  id="name"
                  placeholder="Nguyễn Văn A"
                  value={userInfo.name}
                  onChange={(e) => setUserInfo({...userInfo, name: e.target.value})}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="position">Chức vụ *</Label>
                <Input
                  id="position"
                  placeholder="Chuyên viên, Trưởng phòng..."
                  value={userInfo.position}
                  onChange={(e) => setUserInfo({...userInfo, position: e.target.value})}
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="department">Phòng/Ban</Label>
                <Input
                  id="department"
                  placeholder="Phòng Hành chính - Tổng hợp"
                  value={userInfo.department}
                  onChange={(e) => setUserInfo({...userInfo, department: e.target.value})}
                  className="mt-1"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Document Types */}
        <Card className="mb-6 shadow-lg">
          <CardHeader>
            <CardTitle>Các loại văn bản phổ biến</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {documentTypes.map((type) => (
                <Badge key={type.code} className={`${type.color} text-white px-3 py-1`}>
                  {type.name} ({type.code})
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Workflow Steps */}
        <div className="space-y-6 mb-8">
          {workflowSteps.map((step, index) => {
            const Icon = step.icon;
            const likes = getLikeCount(step.id);
            const dislikes = getDislikeCount(step.id);
            const comments = getComments(step.id);
            
            return (
              <Card key={step.id} className="shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className={`
                  ${step.priority === 'high' ? 'bg-red-50 border-l-4 border-red-500' : 
                    step.priority === 'medium' ? 'bg-yellow-50 border-l-4 border-yellow-500' : 
                    'bg-green-50 border-l-4 border-green-500'}
                `}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="bg-white p-3 rounded-lg shadow">
                        <Icon className="h-6 w-6 text-indigo-600" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="font-mono">
                            Bước {step.id}/8
                          </Badge>
                          {step.priority === 'high' && (
                            <Badge variant="destructive">Quan trọng</Badge>
                          )}
                        </div>
                        <CardTitle className="text-xl mt-1">{step.title}</CardTitle>
                        <CardDescription className="text-sm mt-1">
                          👤 <strong>{step.actor}</strong> • ⏱️ {step.duration}
                        </CardDescription>
                      </div>
                    </div>
                    
                    {/* Feedback buttons */}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleLike(step.id)}
                        className="flex items-center gap-1"
                      >
                        <ThumbsUp className="h-4 w-4" />
                        {likes > 0 && <span>{likes}</span>}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDislike(step.id)}
                        className="flex items-center gap-1"
                      >
                        <ThumbsDown className="h-4 w-4" />
                        {dislikes > 0 && <span>{dislikes}</span>}
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="pt-6">
                  <p className="text-gray-700 mb-4">{step.description}</p>
                  
                  <div className="bg-white rounded-lg border p-4">
                    <h4 className="font-semibold text-sm text-gray-700 mb-2">
                      Công việc cụ thể:
                    </h4>
                    <ul className="space-y-2">
                      {step.tasks.map((task, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                          <span className="text-indigo-500 font-bold">✓</span>
                          <span>{task}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Comments for this step */}
                  {comments.length > 0 && (
                    <div className="mt-4 bg-blue-50 rounded-lg p-4 border border-blue-200">
                      <h4 className="font-semibold text-sm text-blue-900 mb-2 flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Góp ý cho bước này ({comments.length})
                      </h4>
                      <div className="space-y-2">
                        {comments.map((c, idx) => (
                          <div key={idx} className="bg-white p-2 rounded text-sm border border-blue-100">
                            {c.comment}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>

                {/* Connector arrow */}
                {index < workflowSteps.length - 1 && (
                  <div className="flex justify-center py-2">
                    <div className="text-gray-400 text-2xl">↓</div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        {/* Feedback Modal */}
        {showFeedbackForm && activeStep && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-2xl">
              <CardHeader className="bg-gradient-to-r from-orange-500 to-red-600 text-white">
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Góp ý cho Bước {activeStep}
                </CardTitle>
                <CardDescription className="text-orange-100">
                  {workflowSteps.find(s => s.id === activeStep)?.title}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <Label htmlFor="comment" className="text-base">
                  Vui lòng mô tả chi tiết vấn đề hoặc đề xuất cải tiến:
                </Label>
                <Textarea
                  id="comment"
                  placeholder="Ví dụ: Bước này nên có thêm kiểm tra..., Thời gian xử lý quá ngắn/dài..., Đề xuất thêm công cụ hỗ trợ..."
                  value={commentText}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCommentText(e.target.value)}
                  rows={6}
                  className="mt-2"
                />
                <div className="flex gap-2 mt-4">
                  <Button onClick={handleSubmitComment} className="flex-1">
                    Gửi góp ý
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setShowFeedbackForm(false);
                      setActiveStep(null);
                      setCommentText('');
                    }}
                  >
                    Hủy
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Summary & Export */}
        <Card className="shadow-lg bg-gradient-to-r from-green-50 to-blue-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Tổng kết góp ý
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-white p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-blue-600">{workflowSteps.length}</div>
                <div className="text-sm text-gray-600">Tổng số bước</div>
              </div>
              <div className="bg-white p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-green-600">
                  {feedbacks.filter(f => f.type === 'like').length}
                </div>
                <div className="text-sm text-gray-600">Đánh giá tốt</div>
              </div>
              <div className="bg-white p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {feedbacks.filter(f => f.type === 'comment').length}
                </div>
                <div className="text-sm text-gray-600">Góp ý chi tiết</div>
              </div>
              <div className="bg-white p-4 rounded-lg text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round((feedbacks.filter(f => f.type === 'like').length / workflowSteps.length) * 100)}%
                </div>
                <div className="text-sm text-gray-600">Tỷ lệ hài lòng</div>
              </div>
            </div>
            
            {feedbacks.length > 0 && (
              <div className="flex justify-center">
                <Button onClick={handleExportFeedback} className="flex items-center gap-2">
                  <Archive className="h-4 w-4" />
                  Xuất file góp ý (JSON)
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-600 text-sm">
          <p>
            📄 Tài liệu dựa trên: Nghị định 110/2004/NĐ-CP, Thông tư 01/2011/TT-BNV
          </p>
          <p className="mt-1">
            💡 Mọi góp ý xin gửi về: <strong>vanphong@coquan.gov.vn</strong>
          </p>
        </div>
      </div>
    </div>
  );
}
